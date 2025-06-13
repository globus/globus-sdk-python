import logging

from globus_sdk._utils import sha256_string

from .base import StaticGlobusAuthorizer

log = logging.getLogger(__name__)


class AccessTokenAuthorizer(StaticGlobusAuthorizer):
    """
    Implements Authorization using a single Access Token with no Refresh
    Tokens. This is sent as a Bearer token in the header -- basically
    unadorned.

    :param access_token: An access token for Globus Auth
    """

    def __init__(self, access_token: str) -> None:
        log.debug(
            "Setting up an AccessTokenAuthorizer. It will use an "
            "auth type of Bearer and cannot handle 401s."
        )
        self.access_token = access_token
        self.header_val = "Bearer %s" % access_token

        self.access_token_hash = sha256_string(self.access_token)
        log.debug(f'Bearer token has hash "{self.access_token_hash}"')
