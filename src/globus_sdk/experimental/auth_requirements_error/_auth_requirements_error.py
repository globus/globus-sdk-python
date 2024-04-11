from __future__ import annotations

import typing as t

from . import _serializable, _validators


class GlobusAuthorizationParameters(_serializable.Serializable):
    """
    Data class containing authorization parameters that can be passed during
    an authentication flow to control how the user will authenticate.

    When used with a GlobusAuthRequirementsError this represents the additional
    authorization parameters needed in order to complete a request that had
    insufficient authorization state.

    :ivar session_message: A message to be displayed to the user.
    :vartype session_message: str, optional

    :ivar session_required_identities: A list of identities required for the
        session.
    :vartype session_required_identities: list of str, optional

    :ivar session_required_policies: A list of policies required for the
        session.
    :vartype session_required_policies: list of str, optional

    :ivar session_required_single_domain: A list of domains required for the
        session.
    :vartype session_required_single_domain: list of str, optional

    :ivar session_required_mfa: Whether MFA is required for the session.
    :vartype session_required_mfa: bool, optional

    :ivar required_scopes: A list of scopes for which consent is required.
    :vartype required_scopes: list of str, optional

    :ivar prompt: The OIDC 'prompt' parameter, for which Globus Auth currently supports
        the values 'login' and 'none'.
    :vartype prompt: str, optional

    :ivar extra: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra: dict
    """

    def __init__(
        self,
        *,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: list[str] | None = None,
        session_required_single_domain: list[str] | None = None,
        session_required_mfa: bool | None = None,
        required_scopes: list[str] | None = None,
        prompt: str | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.session_message = _validators.opt_str("session_message", session_message)
        self.session_required_identities = _validators.opt_str_list(
            "session_required_identities", session_required_identities
        )
        self.session_required_policies = _validators.opt_str_list(
            "session_required_policies", session_required_policies
        )
        self.session_required_single_domain = _validators.opt_str_list(
            "session_required_single_domain", session_required_single_domain
        )
        self.session_required_mfa = _validators.opt_bool(
            "session_required_mfa", session_required_mfa
        )
        self.required_scopes = _validators.opt_str_list(
            "required_scopes", required_scopes
        )
        self.prompt = _validators.opt_str("prompt", prompt)
        self.extra = extra or {}

        # Enforce that the error contains at least one of the fields we expect
        requires_at_least_one = [
            name for name in self._supported_fields() if name != "session_message"
        ]
        if all(
            getattr(self, field_name) is None for field_name in requires_at_least_one
        ):
            raise _validators.ValidationError(
                "Must include at least one supported authorization parameter: "
                + ", ".join(requires_at_least_one)
            )


class GlobusAuthRequirementsError(_serializable.Serializable):
    """
    Represents a Globus Auth Requirements Error.

    A Globus Auth Requirements Error is a class of error that is returned by Globus
    services to indicate that additional authorization is required in order to complete
    a request and contains information that can be used to request the appropriate
    authorization.

    :ivar code: The error code for this error.
    :vartype code: str

    :ivar authorization_parameters: The authorization parameters for this error.
    :vartype authorization_parameters: GlobusAuthorizationParameters

    :ivar extra: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra: dict
    """

    def __init__(
        self,
        code: str,
        authorization_parameters: dict[str, t.Any] | GlobusAuthorizationParameters,
        *,
        extra: dict[str, t.Any] | None = None,
    ):
        self.code = _validators.str_("code", code)
        self.authorization_parameters = _validators.instance_or_dict(
            "authorization_parameters",
            authorization_parameters,
            GlobusAuthorizationParameters,
        )
        self.extra = extra or {}
