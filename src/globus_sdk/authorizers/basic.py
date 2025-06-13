import base64
import logging

from .base import StaticGlobusAuthorizer

log = logging.getLogger(__name__)


class BasicAuthorizer(StaticGlobusAuthorizer):
    """
    This Authorizer implements Basic Authentication.
    Given a "username" and "password", they are sent base64 encoded in the
    header.

    :param username: Username component for Basic Auth
    :param password: Password component for Basic Auth
    """

    def __init__(self, username: str, password: str) -> None:
        log.debug(
            "Setting up a BasicAuthorizer. It will use an "
            "auth type of Basic and cannot handle 401s."
        )
        log.debug(f"BasicAuthorizer.username = {username}")
        self.username = username
        self.password = password

        to_b64 = f"{username}:{password}"
        self.header_val = f"Basic {_b64str(to_b64)}"


def _b64str(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")
