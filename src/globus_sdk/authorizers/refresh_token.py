import logging

from .renewing import RenewingAuthorizer

log = logging.getLogger(__name__)


class RefreshTokenAuthorizer(RenewingAuthorizer):
    r"""
    Implements Authorization using a Refresh Token to periodically fetch
    renewed Access Tokens. It may be initialized with an Access Token, or it
    will fetch one the first time that ``get_authorization_header()`` is
    called.

    Example usage looks something like this:

    >>> import globus_sdk
    >>> auth_client = globus_sdk.AuthClient(client_id=..., client_secret=...)
    >>> # do some flow to get a refresh token from auth_client
    >>> rt_authorizer = globus_sdk.RefreshTokenAuthorizer(
    >>>     refresh_token, auth_client)
    >>> # create a new client
    >>> transfer_client = globus_sdk.TransferClient(authorizer=rt_authorizer)

    anything that inherits from :class:`BaseClient <globus_sdk.BaseClient>`, so
    at least ``TransferClient`` and ``AuthClient`` will automatically handle
    usage of the ``RefreshTokenAuthorizer``.

    :param refresh_token: Refresh Token for Globus Auth
    :type refresh_token: str
    :param auth_client: ``AuthClient`` capable of using the ``refresh_token``
    :type auth_client: :class:`AuthClient <globus_sdk.AuthClient>`
    :param access_token: Initial Access Token to use, only used if ``expires_at`` is
        also set
    :type access_token: str, optional
    :param expires_at: Expiration time for the starting ``access_token`` expressed as a
        POSIX timestamp (i.e. seconds since the epoch)
    :type expires_at: int, optional
    :param on_refresh: A callback which is triggered any time this authorizer fetches a
        new access_token. The ``on_refresh`` callable is invoked on the
        :class:`OAuthTokenResponse \
        <globus_sdk.services.auth.token_response.OAuthTokenResponse>`
        object resulting from the token being refreshed. It should take only one
        argument, the token response object.
        This is useful for implementing storage for Access Tokens, as the
        ``on_refresh`` callback can be used to update the Access Tokens and
        their expiration times.
    :type on_refresh: callable, optional
    """

    def __init__(
        self,
        refresh_token,
        auth_client,
        access_token=None,
        expires_at=None,
        on_refresh=None,
    ):
        log.info(
            "Setting up RefreshTokenAuthorizer with auth_client="
            f"[instance:{id(auth_client)}]"
        )

        # required for _get_token_data
        self.refresh_token = refresh_token
        self.auth_client = auth_client

        super().__init__(access_token, expires_at, on_refresh)

    def _get_token_response(self):
        """
        Make a refresh token grant
        """
        return self.auth_client.oauth2_refresh_token(self.refresh_token)

    def _extract_token_data(self, res):
        """
        Get the tokens .by_resource_server,
        Ensure that only one token was gotten, and return that token.

        If the token_data includes a "refresh_token" field, update self.refresh_token to
        that value.
        """
        token_data = res.by_resource_server.values()
        if len(token_data) != 1:
            raise ValueError(
                "Attempting refresh for refresh token authorizer "
                "didn't return exactly one token. Possible service error."
            )

        token_data = next(iter(token_data))

        # handle refresh_token being present
        # mandated by OAuth2: https://tools.ietf.org/html/rfc6749#section-6
        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]

        return token_data
