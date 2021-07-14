from typing import Any, Dict, List, Optional, cast


class ErrorInfo:
    """
    Errors may contain "containers" of data which are testable (define ``__bool__``).
    When they have data, they should ``bool()`` as ``True``
    """

    _has_data: bool

    def __bool__(self):
        return self._has_data

    def __str__(self):
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
    :vartype session_message: optional str
    :ivar session_required_identities: A list of identity IDs as strings which are being
        requested by the server
    :vartype session_required_identities: optional list of str
    :ivar session_required_single_domain: A list of domains which are being requested by
        the server ("single domain" because the user should choose one)
    :vartype session_required_single_domain: optional list of str

    **Examples**

    >>> try:
    >>>     ...  # something
    >>> except GlobusAPIError as err:
    >>>     # get a parsed AuthorizationParamaterInfo object, and check if it's truthy
    >>>     authz_params = err.info.authorization_parameters
    >>>     if not authz_params:
    >>>         raise
    >>>     # whatever handling code is desired...
    >>>     print("got authz params:", authz_params)
    """

    def __init__(self, error_data: Dict[str, Any]):
        # data is there if this key is present and it is a dict
        self._has_data = isinstance(error_data.get("authorization_parameters"), dict)
        data = cast(Dict[str, Any], error_data.get("authorization_parameters", {}))

        self.session_message = cast(Optional[str], data.get("session_message"))
        self.session_required_identities = cast(
            Optional[List[str]], data.get("session_required_identities")
        )
        self.session_required_single_domain = cast(
            Optional[List[str]], data.get("session_required_single_domain")
        )


class ConsentRequiredInfo(ErrorInfo):
    """
    ConsentRequiredInfo objects contain required consent information for an error. They
    test as truthy if the error was marked as a ConsentRequired error.

    :ivar required_scopes: A list of scopes requested by the server
    :vartype required_scopes: optional list of str
    """

    def __init__(self, error_data: Dict[str, Any]):
        # data is only considered parseable if this error has the code 'ConsentRequired'
        has_code = error_data.get("code") == "ConsentRequired"
        data = error_data if has_code else {}
        self.required_scopes = cast(Optional[List[str]], data.get("required_scopes"))

        # but the result is only considered valid if both parts are present
        self._has_data = has_code and isinstance(self.required_scopes, list)


class ErrorInfoContainer:
    """
    This is a wrapper type which contains various error info objects for parsed error
    data. It is attached to API errors as the ``.info`` attribute.

    :ivar authorization_parameters: A parsed AuthorizationParameterInfo object
    :ivar consent_required: A parsed ConsentRequiredInfo object
    """

    def __init__(self, error_data: Optional[Dict[str, Any]]):
        self.authorization_parameters = AuthorizationParameterInfo(error_data or {})
        self.consent_required = ConsentRequiredInfo(error_data or {})

    def __str__(self):
        return f"{self.authorization_parameters}|{self.consent_required}"
