from __future__ import annotations

import abc
import logging
import time
import typing as t

from globus_sdk import exc
from globus_sdk._utils import sha256_string

from .base import GlobusAuthorizer

if t.TYPE_CHECKING:
    from globus_sdk.services.auth import OAuthTokenResponse

log = logging.getLogger(__name__)
# Provides a buffer for token expiration time to account for
# possible delays or clock skew.
EXPIRES_ADJUST_SECONDS = 60

# the type of the response which is produced by the authorizer, received by it, and
# passed to the `on_refresh` callback
ResponseT = t.TypeVar("ResponseT", bound="OAuthTokenResponse")


class RenewingAuthorizer(GlobusAuthorizer, t.Generic[ResponseT], metaclass=abc.ABCMeta):
    r"""
    A ``RenewingAuthorizer`` is an abstract superclass to any authorizer
    that needs to get new Access Tokens in order to form Authorization headers.

    It may be passed an initial Access Token, but if so must also be passed
    an expires_at value for that token.

    It provides methods that handle the logic for checking and adjusting
    expiration time, callbacks on renewal, and 401 handling.

    To make an authorizer that implements this class implement
    the _get_token_response and _extract_token_data methods for that
    authorization type,

    :param access_token: Initial Access Token to use, only used if ``expires_at`` is
        also set
    :param expires_at: Expiration time for the starting ``access_token`` expressed as a
        POSIX timestamp (i.e. seconds since the epoch)
    :param on_refresh: A callback which is triggered any time this authorizer fetches a
        new access_token. The ``on_refresh`` callable is invoked on the response
        object resulting from the token being refreshed. It should take only one
        argument, the token response object.
        This is useful for implementing storage for Access Tokens, as the
        ``on_refresh`` callback can be used to update the Access Tokens and
        their expiration times.
    """

    def __init__(
        self,
        access_token: str | None = None,
        expires_at: int | None = None,
        on_refresh: None | t.Callable[[ResponseT], t.Any] = None,
    ) -> None:
        self._access_token = None
        self._access_token_hash = None

        log.debug(
            "Setting up a RenewingAuthorizer. It will use an "
            "auth type of Bearer and can handle 401s."
        )

        if (access_token is not None and expires_at is None) or (
            access_token is None and expires_at is not None
        ):
            raise exc.GlobusSDKUsageError(
                "A RenewingAuthorizer cannot be initialized with one of "
                "access_token and expires_at. Either provide both or neither."
            )

        self.access_token = access_token
        self.expires_at = expires_at
        self.on_refresh = on_refresh

        if self.access_token is not None:
            log.debug(
                "RenewingAuthorizer will start by using access_token "
                f'with hash "{self._access_token_hash}"'
            )
        # if data were unspecified, fetch a new access token
        else:
            log.debug(
                "Creating RenewingAuthorizer without Access "
                "Token. Fetching initial token now."
            )
            self._get_new_access_token()

    @property
    def access_token(self) -> str | None:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        self._access_token = value
        if value:
            self._access_token_hash = sha256_string(value)

    @abc.abstractmethod
    def _get_token_response(self) -> ResponseT:
        """
        Using whatever method the specific authorizer implementing this class
        does, get a new token response.
        """

    @abc.abstractmethod
    def _extract_token_data(self, res: ResponseT) -> dict[str, t.Any]:
        """
        Given a token response object, get the first element of
        token_response.by_resource_server
        This method is expected to enforce that by_resource_server is only
        returning one access token, and return a ValueError otherwise.
        """

    def _get_new_access_token(self) -> None:
        """
        Given token data from _get_token_response and _extract_token_data,
        set the access token and expiration time, calculate the new token
        hash, and call on_refresh
        """
        # get the first (and only) token
        res = self._get_token_response()
        token_data = self._extract_token_data(res)

        self.expires_at = token_data["expires_at_seconds"]
        self.access_token = token_data["access_token"]

        log.debug(
            "RenewingAuthorizer.access_token updated to "
            f'token with hash "{self._access_token_hash}"'
        )

        if callable(self.on_refresh):
            log.debug("will call on_refresh callback")
            self.on_refresh(res)
            log.debug("on_refresh callback finished")

    def ensure_valid_token(self) -> None:
        """
        Check that the authorizer has a valid token. Checks that the token is set and
        that the expiration time is in the future.

        This is called implicitly by ``get_authorization_header``, but you can
        call it explicitly if you want to ensure that a token gets refreshed.
        This can be useful in order to get at a new, valid token via the
        ``on_refresh`` handler.
        """
        log.debug("RenewingAuthorizer checking expiration time")
        if self.access_token is None:
            log.debug("RenewingAuthorizer has no token")
        else:
            if (
                self.expires_at is not None
                and time.time() <= self.expires_at - EXPIRES_ADJUST_SECONDS
            ):
                log.debug("RenewingAuthorizer determined time has not yet expired")
                return
            else:
                log.debug("RenewingAuthorizer has a token, but it is expired")

        log.debug("RenewingAuthorizer fetching new Access Token")
        self._get_new_access_token()

    def get_authorization_header(self) -> str:
        """
        Check to see if a new token is needed and return "Bearer <access_token>"
        """
        self.ensure_valid_token()
        log.debug(f'bearer token has hash "{self._access_token_hash}"')
        return f"Bearer {self.access_token}"

    def handle_missing_authorization(self) -> bool:
        """
        The renewing authorizer can respond to a service 401 by immediately
        invalidating its current Access Token. When this happens, the next call
        to ``set_authorization_header()`` will result in a new Access Token
        being fetched.
        """
        log.debug(
            "RenewingAuthorizer seeing 401. Invalidating "
            "token and preparing for refresh."
        )
        # None for expires_at invalidates any current token
        self.expires_at = None
        # respond True, as in "we took some action, the 401 *may* be resolved"
        return True
