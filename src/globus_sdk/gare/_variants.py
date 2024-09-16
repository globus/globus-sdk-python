from __future__ import annotations

import sys
import typing as t

from globus_sdk import exc
from globus_sdk._guards import validators
from globus_sdk._serializable import Serializable

from ._auth_requirements_error import GARE, GlobusAuthorizationParameters

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

V = t.TypeVar("V", bound="LegacyAuthRequirementsErrorVariant")


class LegacyAuthRequirementsErrorVariant(Protocol):
    """
    Protocol for errors which can be converted to a Globus Auth Requirements Error.
    """

    @classmethod
    def from_dict(cls: type[V], data: dict[str, t.Any]) -> V:
        pass

    def to_auth_requirements_error(self) -> GARE: ...


class LegacyConsentRequiredTransferError(Serializable):
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scopes: list[str],
        extra: dict[str, t.Any] | None = None,
    ):
        self.code = _validate_consent_required_literal("code", code)
        self.required_scopes = validators.str_list("required_scopes", required_scopes)
        self.extra = extra or {}

    def to_auth_requirements_error(self) -> GARE:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        return GARE(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                required_scopes=self.required_scopes,
                session_message=self.extra.get("message"),
            ),
            extra=self.extra,
        )


class LegacyConsentRequiredAPError(Serializable):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scope: str,
        extra: dict[str, t.Any] | None,
    ):
        self.code = _validate_consent_required_literal("code", code)
        self.required_scope = validators.str_("required_scope", required_scope)
        self.extra = extra or {}

    def to_auth_requirements_error(self) -> GARE:
        """
        Return a GlobusAuthRequirementsError representing this error.

        Normalizes the required_scope field to a list and uses the description
        to set the session message.
        """
        return GARE(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                required_scopes=[self.required_scope],
                session_message=self.extra.get("description"),
                extra=self.extra.get("authorization_parameters"),
            ),
            extra={
                k: v for k, v in self.extra.items() if k != "authorization_parameters"
            },
        )


class LegacyAuthorizationParameters(Serializable):
    """
    An Authorization Parameters object that describes all known variants in use by
    Globus services.
    """

    def __init__(
        self,
        *,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: str | list[str] | None = None,
        session_required_single_domain: str | list[str] | None = None,
        session_required_mfa: bool | None = None,
        prompt: Literal["login"] | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.session_message = validators.opt_str("session_message", session_message)
        self.session_required_identities = validators.opt_str_list(
            "session_required_identities", session_required_identities
        )
        self.session_required_policies = validators.opt_str_list_or_commasep(
            "session_required_policies", session_required_policies
        )
        self.session_required_single_domain = validators.opt_str_list_or_commasep(
            "session_required_single_domain", session_required_single_domain
        )
        self.session_required_mfa = validators.opt_bool(
            "session_required_mfa", session_required_mfa
        )
        if prompt in [None, "login"]:
            self.prompt = prompt
        else:
            raise exc.ValidationError("'prompt' must be 'login' or null")
        self.extra = extra or {}

    def to_authorization_parameters(
        self,
    ) -> GlobusAuthorizationParameters:
        """
        Return a normalized GlobusAuthorizationParameters instance representing
        these parameters.

        Normalizes fields that may have been provided
        as comma-delimited strings to lists of strings.
        """
        return GlobusAuthorizationParameters(
            session_message=self.session_message,
            session_required_identities=self.session_required_identities,
            session_required_mfa=self.session_required_mfa,
            session_required_policies=self.session_required_policies,
            session_required_single_domain=self.session_required_single_domain,
            prompt=self.prompt,
            extra=self.extra,
        )


class LegacyAuthorizationParametersError(Serializable):
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"

    def __init__(
        self,
        *,
        authorization_parameters: dict[str, t.Any] | LegacyAuthorizationParameters,
        code: str | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        # Apply default, if necessary
        self.code = validators.str_("code", code or self.DEFAULT_CODE)
        self.authorization_parameters = validators.instance_or_dict(
            "authorization_parameters",
            authorization_parameters,
            LegacyAuthorizationParameters,
        )
        self.extra = extra or {}

    def to_auth_requirements_error(self) -> GARE:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        authorization_parameters = (
            self.authorization_parameters.to_authorization_parameters()
        )
        return GARE(
            authorization_parameters=authorization_parameters,
            code=self.code,
            extra=self.extra,
        )


def _validate_consent_required_literal(
    name: str, value: t.Any
) -> Literal["ConsentRequired"]:
    if value == "ConsentRequired":
        return "ConsentRequired"
    raise exc.ValidationError(f"'{name}' must be the string 'ConsentRequired'")
