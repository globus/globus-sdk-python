import globus_sdk.gare


def coalesce(
    *gares: globus_sdk.gare.GARE,
    session_message: str | None = None,
    prompt: str | None = None,
) -> list[globus_sdk.gare.GARE]:
    # build a list of GARE fields which are allowed to merge
    safe_fields = ["session_required_policies", "required_scopes"]
    if session_message is not None:
        safe_fields.append("session_message")
    if prompt is not None:
        safe_fields.append("prompt")

    # Build lists of GAREs that can and cannot be merged
    candidates, non_candidates = [], []
    for g in gares:
        if _is_candidate(g, safe_fields):
            candidates.append(g)
        else:
            non_candidates.append(g)

    # if no GAREs were safe to merge, return early
    if not candidates:
        return non_candidates

    # merge safe GAREs and override any provided field values
    combined = _safe_combine(candidates)
    if session_message is not None:
        combined.authorization_parameters.session_message = session_message
    if prompt is not None:
        combined.authorization_parameters.prompt = prompt

    # return the reduced list of GAREs
    return [combined] + non_candidates


def _is_candidate(g: globus_sdk.gare.GARE, safe_fields: list[str]) -> bool:
    params = g.authorization_parameters

    # check all of the supported GARE fields
    for field_name in (
        "session_message",
        "session_required_identities",
        "session_required_policies",
        "session_required_single_domain",
        "session_required_mfa",
        "required_scopes",
        "prompt",
    ):
        # if the field is considered safe, ignore it
        if field_name in safe_fields:
            continue
        # if the field isn't considered safe and it is set,
        # then the GARE shouldn't be merged
        if getattr(params, field_name) is not None:
            return False

    # if we didn't find any invalidating fields, it must be safe to merge
    return True


def _safe_combine(mergeable_gares: list[globus_sdk.gare.GARE]) -> globus_sdk.gare.GARE:
    code = "AuthorizationRequired"
    if all(g.code == "ConsentRequired" for g in mergeable_gares):
        code = "ConsentRequired"

    combined_params = globus_sdk.gare.GlobusAuthorizationParameters(
        session_required_policies=_concat(
            [
                g.authorization_parameters.session_required_policies
                for g in mergeable_gares
            ]
        ),
        required_scopes=_concat(
            [g.authorization_parameters.required_scopes for g in mergeable_gares]
        ),
    )

    return globus_sdk.gare.GARE(code=code, authorization_parameters=combined_params)


def _concat(values: list[list[str] | None]) -> list[str] | None:
    if all(v is None for v in values):
        return None

    return [element for value in values if value is not None for element in value]


if __name__ == "__main__":
    # these are example errors
    case1 = globus_sdk.gare.to_gare(
        {
            "code": "ConsentRequired",
            "authorization_parameters": {"required_scopes": ["foo"]},
        }
    )
    case2 = globus_sdk.gare.to_gare(
        {
            "code": "ConsentRequired",
            "authorization_parameters": {"required_scopes": ["bar"]},
        }
    )
    case3 = globus_sdk.gare.to_gare(
        {
            "code": "AuthorizationRequired",
            "authorization_parameters": {"required_scopes": ["baz"]},
        }
    )
    case4 = globus_sdk.gare.to_gare(
        {
            "code": "AuthorizationRequired",
            "authorization_parameters": {
                "session_required_policies": [
                    "f2047039-2f07-4f13-b21b-b2edf7f9d329",
                    "2fc6d9a3-9322-48a1-ad39-5dcf63a593a7",
                ],
            },
        }
    )
    case5 = globus_sdk.gare.to_gare(
        {
            "code": "AuthorizationRequired",
            "authorization_parameters": {
                "session_required_policies": [
                    "f2047039-2f07-4f13-b21b-b2edf7f9d329",
                    "2fc6d9a3-9322-48a1-ad39-5dcf63a593a7",
                ],
                "session_required_mfa": True,
            },
        }
    )
    case6 = globus_sdk.gare.to_gare(
        {
            "code": "AuthorizationRequired",
            "authorization_parameters": {
                "session_required_policies": ["ba10f6f1-5b23-4703-bfb7-4fdd7b529546"],
                "session_message": "needs a policy",
            },
        }
    )
    case7 = globus_sdk.gare.to_gare(
        {
            "code": "AuthorizationRequired",
            "authorization_parameters": {
                "session_required_policies": ["ba10f6f1-5b23-4703-bfb7-4fdd7b529546"],
                "prompt": "login",
            },
        }
    )

    print("\n--full merge--\n")
    print("\ncombining two:")
    for g in coalesce(case1, case2):
        print(" -", g)
    print("\ncombining three:")
    for g in coalesce(case1, case2, case3):
        print(" -", g)
    print("\ncombining four:")
    for g in coalesce(case1, case2, case3, case4):
        print(" -", g)

    print("\n--no merge--\n")
    print("\ncombining two:")
    for g in coalesce(case1, case5):
        print(" -", g)
    print("\ncombining two:")
    for g in coalesce(case4, case5):
        print(" -", g)
    print("\ncombining two:")
    for g in coalesce(case2, case6):
        print(" -", g)
    print("\ncombining two:")
    for g in coalesce(case4, case7):
        print(" -", g)

    print("\n--merge due to explicit param--\n")
    print("\ncombining two:")
    for g in coalesce(case1, case6, session_message="explicit message"):
        print(" -", g)
    print("\ncombining two:")
    for g in coalesce(case4, case7, prompt="login"):
        print(" -", g)
