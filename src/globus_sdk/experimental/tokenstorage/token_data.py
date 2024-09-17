from __future__ import annotations

import typing as t

from globus_sdk._guards import validators
from globus_sdk._serializable import Serializable


class TokenStorageData(Serializable):
    """
    Data class containing tokens and metadata for a specific resource server used
    as the python interface for ``TokenStorage``.
    Contains the following attributes:

    resource_server: str
    The name of the resource server this token data is valid for

    identity_id: str
    A UUID string for the user this token data was granted to. This value may
    be None if the original token grant did not include the "openid" scope

    scope: str
    A space separated list of scopes these tokens provide access to.

    access_token: str
    An access token that can be used for authentication with Globus APIs.

    refresh_token: str | None
    A refresh token that can be used for refresh token grants. This value may be
    None if the original token grant did not allow for refresh tokens.

    expires_at_seconds: int
    A POSIX timestamp for the time when access_token expires.

    token_type: str | None
    The token type of access_token, currently this will always be "Bearer" if present

    extra: dict | None
    A dictionary of additional fields that were provided. May be used for
    forward/backward compatibility.
    """

    def __init__(
        self,
        resource_server: str,
        identity_id: str | None,
        scope: str,
        access_token: str,
        refresh_token: str | None,
        expires_at_seconds: int,
        token_type: str | None,
        extra: dict[str, t.Any] | None = None,
    ) -> None:
        self.resource_server = validators.str_("resource_server", resource_server)
        self.identity_id = validators.opt_str("identity_id", identity_id)
        self.scope = validators.str_("scope", scope)
        self.access_token = validators.str_("access_token", access_token)
        self.refresh_token = validators.opt_str("refresh_token", refresh_token)
        self.expires_at_seconds = validators.int_(
            "expires_at_seconds", expires_at_seconds
        )
        self.token_type = validators.opt_str("token_type", token_type)
        self.extra = extra or {}
