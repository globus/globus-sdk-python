from __future__ import annotations

import typing as t

from globus_sdk._guards import validators
from globus_sdk._serializable import Serializable


class TokenStorageData(Serializable):
    """
    Data class for tokens and token metadata issued by a globus auth token grant.
    For storage and retrieval of these objects, see :class:`TokenStorage`.

    Tokens are scoped to a specific user/client (`identity_id`) performing
    specific operations (`scope`) with a specific service (`resource_server`).

    :ivar str resource_server: The resource server for which this token data was
        granted.

    :ivar str identity_id: The primary identity id of the user or client which
        requested this token. This will be None if an identity id was not extractable
        from the token grant response.

    :ivar str scope: A space separated list of scopes that this token data provides
        access to.

    :ivar str access_token: A Globus Auth-issued OAuth2 access token. Used for
        authentication when interacting with service APIs.

    :ivar str | None refresh_token: A Globus Auth-issued OAuth2 refresh token. Used to
        obtain new access tokens when the current one expires. This value will be None
        if the original token grant did not request refresh tokens.

    :ivar int expires_at_seconds: An epoch seconds timestamp for when the associated
        access_token expires.

    :ivar str | None token_type: The token type of access_token, currently this will
        always be "Bearer" if present.

    :param extra: An optional dictionary of additional fields to include. Included for
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
