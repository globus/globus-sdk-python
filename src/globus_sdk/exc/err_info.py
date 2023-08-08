from __future__ import annotations

import logging
import typing as t

from globus_sdk import _guards

log = logging.getLogger(__name__)


class ErrorInfo:
    """
    Errors may contain "containers" of data which are testable (define ``__bool__``).
    When they have data, they should ``bool()`` as ``True``
    """

    _has_data: bool

    def __bool__(self) -> bool:
        return self._has_data

    def __str__(self) -> str:
        if self:
            attrmap = ", ".join(
                [f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")]
            )
        else:
            attrmap = ":"
        return f"{self.__class__.__name__}({attrmap})"


class AuthorizationParameterInfo(ErrorInfo):
    """
    AuthorizationParameterInfo objects may contain information about the
    'authorization_parameters' of an error. They test as truthy when the error has valid
    'authorization_parameters' data.

    :ivar session_message: A message from the server
    :vartype session_message: str, optional
    :ivar session_required_identities: A list of identity IDs as strings which are being
        requested by the server
    :vartype session_required_identities: list of str, optional
    :ivar session_required_single_domain: A list of domains which are being requested by
        the server ("single domain" because the user should choose one)
    :vartype session_required_single_domain: list of str, optional

    **Examples**

    >>> try:
    >>>     ...  # something
    >>> except GlobusAPIError as err:
    >>>     # get a parsed AuthorizationParameterInfo object, and check if it's truthy
    >>>     authz_params = err.info.authorization_parameters
    >>>     if not authz_params:
    >>>         raise
    >>>     # whatever handling code is desired...
    >>>     print("got authz params:", authz_params)
    """

    def __init__(self, error_data: dict[str, t.Any]):
        # data is there if this key is present and it is a dict
        self._has_data = isinstance(error_data.get("authorization_parameters"), dict)
        data = t.cast(
            t.Dict[str, t.Any], error_data.get("authorization_parameters", {})
        )

        self.session_message: str | None = self._parse_session_message(data)

        self.session_required_identities: (
            list[str] | None
        ) = self._parse_session_required_identities(data)

        self.session_required_single_domain: (
            list[str] | None
        ) = self._parse_session_required_single_domain(data)

        self.session_required_policies: (
            list[str] | None
        ) = self._parse_session_required_policies(data)

    def _parse_session_message(self, data: dict[str, t.Any]) -> str | None:
        session_message = data.get("session_message")
        if isinstance(session_message, str):
            return session_message
        elif session_message is not None:
            self._warn_type("session_message", "str", session_message)
        return None

    def _parse_session_required_identities(
        self, data: dict[str, t.Any]
    ) -> list[str] | None:
        session_required_identities = data.get("session_required_identities")
        if _guards.is_list_of(session_required_identities, str):
            return session_required_identities
        elif session_required_identities is not None:
            self._warn_type(
                "session_required_identities",
                "list[str]",
                session_required_identities,
            )
        return None

    def _parse_session_required_single_domain(
        self, data: dict[str, t.Any]
    ) -> list[str] | None:
        session_required_single_domain = data.get("session_required_single_domain")
        if _guards.is_list_of(session_required_single_domain, str):
            return session_required_single_domain
        elif session_required_single_domain is not None:
            self._warn_type(
                "session_required_single_domain",
                "list[str]",
                session_required_single_domain,
            )
        return None

    def _parse_session_required_policies(
        self, data: dict[str, t.Any]
    ) -> list[str] | None:
        session_required_policies = data.get("session_required_policies")
        if isinstance(session_required_policies, str):
            return session_required_policies.split(",")
        elif _guards.is_list_of(session_required_policies, str):
            return session_required_policies
        elif session_required_policies is not None:
            self._warn_type(
                "session_required_policies", "list[str]|str", session_required_policies
            )
        return None

    def _warn_type(self, key: str, expected: str, got: t.Any) -> None:
        log.warning(
            f"During ErrorInfo instantiation, got unexpected type for '{key}'. "
            f"Expected '{expected}'. Got '{got}'"
        )


class ConsentRequiredInfo(ErrorInfo):
    """
    ConsentRequiredInfo objects contain required consent information for an error. They
    test as truthy if the error was marked as a ConsentRequired error.

    :ivar required_scopes: A list of scopes requested by the server
    :vartype required_scopes: list of str, optional
    """

    def __init__(self, error_data: dict[str, t.Any]) -> None:
        # data is only considered parseable if this error has the code 'ConsentRequired'
        has_code = error_data.get("code") == "ConsentRequired"
        data = error_data if has_code else {}
        self.required_scopes = self._parse_required_scopes(data)

        # but the result is only considered valid if both parts are present
        self._has_data = has_code and bool(self.required_scopes)

    def _parse_required_scopes(self, data: dict[str, t.Any]) -> list[str]:
        if _guards.is_list_of(data.get("required_scopes"), str):
            return t.cast("list[str]", data["required_scopes"])
        elif isinstance(data.get("required_scope"), str):
            return [data["required_scope"]]
        return []


class ErrorInfoContainer:
    """
    This is a wrapper type which contains various error info objects for parsed error
    data. It is attached to API errors as the ``.info`` attribute.

    :ivar authorization_parameters: A parsed AuthorizationParameterInfo object
    :ivar consent_required: A parsed ConsentRequiredInfo object
    """

    def __init__(self, error_data: dict[str, t.Any] | None) -> None:
        self.authorization_parameters = AuthorizationParameterInfo(error_data or {})
        self.consent_required = ConsentRequiredInfo(error_data or {})

    def __str__(self) -> str:
        return f"{self.authorization_parameters}|{self.consent_required}"
