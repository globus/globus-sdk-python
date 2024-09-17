from __future__ import annotations

import logging
import typing as t

import globus_sdk

from .renewing import RenewingAuthorizer

log = logging.getLogger(__name__)


class RefreshTokenAuthorizer(
    RenewingAuthorizer["globus_sdk.OAuthRefreshTokenResponse"]
):
    """
    Implements Authorization using a Refresh Token to periodically fetch
    renewed Access Tokens. It may be initialized with an Access Token, or it
    will fetch one the first time that ``get_authorization_header()`` is
    called.

    Example usage looks something like this:

    .. code-block:: pycon

        >>> import globus_sdk
        >>> auth_client = globus_sdk.ConfidentialAppAuthClient(client_id=..., client_secret=...)
        >>> # do some flow to get a refresh token from auth_client
        >>> rt_authorizer = globus_sdk.RefreshTokenAuthorizer(refresh_token, auth_client)
        >>> # create a new client
        >>> transfer_client = globus_sdk.TransferClient(authorizer=rt_authorizer)

    Anything which inherits from :class:`BaseClient <globus_sdk.BaseClient>`
    will automatically support usage of the ``RefreshTokenAuthorizer``.

    :param refresh_token: Refresh Token for Globus Auth
    :param auth_client: ``AuthClient`` capable of using the ``refresh_token``
    :param access_token: Initial Access Token to use, only used if ``expires_at`` is
        also set
    :param expires_at: Expiration time for the starting ``access_token`` expressed as a
        POSIX timestamp (i.e. seconds since the epoch)
    :param on_refresh: A callback which is triggered any time this authorizer fetches a
        new access_token. The ``on_refresh`` callable is invoked on the
        :class:`globus_sdk.OAuthRefreshTokenResponse` object resulting from the token being
        refreshed. It should take only one argument, the token response object.
        This is useful for implementing storage for Access Tokens, as the
        ``on_refresh`` callback can be used to update the Access Tokens and
        their expiration times.
    """  # noqa: E501

    def __init__(
        self,
        refresh_token: str,
        auth_client: globus_sdk.AuthLoginClient,
        *,
        access_token: str | None = None,
        expires_at: int | None = None,
        on_refresh: (
            None | t.Callable[[globus_sdk.OAuthRefreshTokenResponse], t.Any]
        ) = None,
    ):
        log.info(
            "Setting up RefreshTokenAuthorizer with auth_client="
            f"[instance:{id(auth_client)}]"
        )
        # per type checkers, this is unreachable... but it is, of course, reachable...
        # that's... the point
        if isinstance(auth_client, globus_sdk.AuthClient):  # type: ignore[unreachable]
            raise globus_sdk.GlobusSDKUsageError(
                "RefreshTokenAuthorizer requires an AuthLoginClient, not an "
                "AuthClient. In past versions of the SDK, it was possible to "
                "use an AuthClient if it was correctly authorized, but this is "
                "no longer allowed. "
                "Proper usage should typically use a NativeAppAuthClient or "
                "ConfidentialAppAuthClient."
            )

        # required for _get_token_data
        self.refresh_token = refresh_token
        self.auth_client = auth_client

        super().__init__(access_token, expires_at, on_refresh)

    def _get_token_response(self) -> globus_sdk.OAuthRefreshTokenResponse:
        """
        Make a refresh token grant
        """
        return self.auth_client.oauth2_refresh_token(self.refresh_token)

    def _extract_token_data(
        self, res: globus_sdk.OAuthRefreshTokenResponse
    ) -> dict[str, t.Any]:
        """
        Get the tokens .by_resource_server,
        Ensure that only one token was gotten, and return that token.

        If the token_data includes a "refresh_token" field, update self.refresh_token to
        that value.
        """
        token_data_list = list(res.by_resource_server.values())
        if len(token_data_list) != 1:
            raise ValueError(
                "Attempting refresh for refresh token authorizer "
                "didn't return exactly one token. Possible service error."
            )

        token_data = next(iter(token_data_list))

        # handle refresh_token being present
        # mandated by OAuth2: https://tools.ietf.org/html/rfc6749#section-6
        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]

        return token_data
