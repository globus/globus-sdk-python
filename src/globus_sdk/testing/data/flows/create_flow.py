from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC

_two_hop_transfer_create_request = {
    k: TWO_HOP_TRANSFER_FLOW_DOC[k]
    for k in [
        "title",
        "definition",
        "input_schema",
        "subtitle",
        "description",
        "flow_viewers",
        "flow_starters",
        "flow_administrators",
        "run_managers",
        "run_monitors",
        "keywords",
    ]
}
RESPONSES = ResponseSet(
    metadata={
        "params": _two_hop_transfer_create_request,
    },
    default=RegisteredResponse(
        service="flows",
        path="/flows",
        method="POST",
        json=TWO_HOP_TRANSFER_FLOW_DOC,
    ),
    bad_admin_principal_error=RegisteredResponse(
        service="flows",
        path="/flows",
        method="POST",
        status=422,
        json={
            "error": {
                "code": "UNPROCESSABLE_ENTITY",
                "detail": [
                    {
                        "loc": ["flow_administrators", 0],
                        "msg": (
                            "Unrecognized principal string: "
                            '"ae341a98-d274-11e5-b888-dbae3a8ba545". '
                            'Allowed principal types in role "FlowAdministrator": '
                            "[<AuthGroupUrn>, <AuthIdentityUrn>]"
                        ),
                        "type": "value_error",
                    },
                    {
                        "loc": ["flow_administrators", 1],
                        "msg": (
                            "Unrecognized principal string: "
                            '"4fab4345-6d20-43a0-9a25-16b2e3bbe765". '
                            'Allowed principal types in role "FlowAdministrator": '
                            "[<AuthGroupUrn>, <AuthIdentityUrn>]"
                        ),
                        "type": "value_error",
                    },
                ],
            },
            "debug_id": "cf71b1d1-ab7e-48b1-8c54-764201d28ded",
        },
    ),
)
