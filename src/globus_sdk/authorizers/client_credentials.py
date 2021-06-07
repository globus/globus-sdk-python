import logging

from .renewing import RenewingAuthorizer

log = logging.getLogger(__name__)


class ClientCredentialsAuthorizer(RenewingAuthorizer):
    r"""
    Implementation of a RenewingAuthorizer that renews confidential app client
    Access Tokens using a ConfidentialAppAuthClient and a set of scopes to
    fetch a new Access Token when the old one expires.

    Example usage looks something like this:

    >>> import globus_sdk
    >>> confidential_client = globus_sdk.ConfidentialAppAuthClient(
        client_id=..., client_secret=...)
    >>> scopes = "..."
    >>> cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
    >>>     confidential_client, scopes)
    >>> # create a new client
    >>> transfer_client = globus_sdk.TransferClient(authorizer=cc_authorizer)

    any client that inherits from :class:`BaseClient <globus_sdk.BaseClient>`
    should be able to use a ClientCredentialsAuthorizer to act as
    the client itself.

    :param confidential_client: client object with a valid id and client secret
    :type confidential_client: :class:`ConfidentialAppAuthClient\
        <globus_sdk.ConfidentialAppAuthClient>`
    :param scopes: A string of space-separated scope names being requested for the
        access tokens that will be used for the Authorization header. These scopes must
        all be for the same resource server, or else the token response will have
        multiple access tokens.
    :type scopes: str
    :param access_token: Initial Access Token to use, only used if ``expires_at`` is
        also set. Must be requested with the same set of scopes passed to this
        authorizer.
    :type access_token: str
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
    :type on_refresh: callable, optiona
    """

    def __init__(
        self,
        confidential_client,
        scopes,
        access_token=None,
        expires_at=None,
        on_refresh=None,
    ):
        log.info(
            "Setting up ClientCredentialsAuthorizer with confidential_client="
            f"[instance:{id(confidential_client)}] and scopes={scopes}"
        )

        # values for _get_token_data
        self.confidential_client = confidential_client
        self.scopes = scopes

        super().__init__(access_token, expires_at, on_refresh)

    def _get_token_response(self):
        """
        Make a client credentials grant
        """
        return self.confidential_client.oauth2_client_credentials_tokens(
            requested_scopes=self.scopes
        )

    def _extract_token_data(self, res):
        """
        Get the tokens .by_resource_server,
        Ensure that only one token was gotten, and return that token.
        """
        token_data = res.by_resource_server.values()
        if len(token_data) != 1:
            raise ValueError(
                "Attempting get new access token for client credentials "
                "authorizer didn't return exactly one token. Ensure scopes "
                f"{self.scopes} are for only one resource server."
            )

        return next(iter(token_data))
