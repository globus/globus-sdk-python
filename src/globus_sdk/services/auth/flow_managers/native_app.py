from __future__ import annotations

import base64
import hashlib
import logging
import os
import re
import typing as t
import urllib.parse

from globus_sdk._missing import MISSING, MissingType, filter_missing
from globus_sdk._types import ScopeCollectionType
from globus_sdk._utils import slash_join
from globus_sdk.exc import GlobusSDKUsageError

from .._common import stringify_requested_scopes
from ..response import OAuthAuthorizationCodeResponse
from .base import GlobusOAuthFlowManager

if t.TYPE_CHECKING:
    import globus_sdk

log = logging.getLogger(__name__)


def _make_native_app_challenge(
    verifier: str | MissingType = MISSING,
) -> tuple[str, str]:
    """
    Produce a challenge and verifier for the Native App flow.
    The verifier is an unhashed secret, and the challenge is a hashed version
    of it. The challenge is sent at the start of the flow, and the secret is
    sent at the end, proving that the same client that started the flow is
    continuing it.

    Hashing is always done with simple SHA256.

    See RFC 7636 for details.

    :param verifier: The code verifier string used to construct the code challenge. Must
        be at least 43 characters long and not longer than 128 characters. Must only
        contain the following characters: [a-zA-Z0-9~_.-].
    """

    if isinstance(verifier, str):
        if not 43 <= len(verifier) <= 128:
            raise GlobusSDKUsageError(
                f"verifier must be 43-128 characters long: {len(verifier)}"
            )
        if bool(re.search(r"[^a-zA-Z0-9~_.-]", verifier)):
            raise GlobusSDKUsageError("verifier contained invalid characters")

        code_verifier: str = verifier
    else:
        log.debug(
            "Autogenerating verifier secret. On low-entropy systems "
            "this may be insecure"
        )
        code_verifier = (
            base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
        )

    # hash it, pull out a digest
    hashed_verifier = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    # urlsafe base64 encode that hash and strip the padding
    code_challenge = (
        base64.urlsafe_b64encode(hashed_verifier).decode("utf-8").rstrip("=")
    )

    # return the verifier and the encoded hash
    return code_verifier, code_challenge


class GlobusNativeAppFlowManager(GlobusOAuthFlowManager):
    """
    This is the OAuth flow designated for use by clients wishing to
    authenticate users in the absence of a Client Secret. Because these
    applications run "natively" in the user's environment, they cannot
    protect a secret.
    Instead, a temporary secret is generated solely for this authentication
    attempt.

    :param auth_client: The client object on which this flow is based.
        It is used to extract default values for the flow, and also to make calls to the
        Auth service.
    :param requested_scopes: The scopes on the token(s) being requested.
    :param redirect_uri: The page that users should be directed to after authenticating
        at the authorize URL. Defaults to 'https://auth.globus.org/v2/web/auth-code',
        which displays the resulting ``auth_code`` for users to copy-paste back into
        your application (and thereby be passed back to the
        ``GlobusNativeAppFlowManager``)
    :param state: The ``redirect_uri`` page will have this included in a query
        parameter, so you can use it to pass information to that page if you use a
        custom page. It defaults to the string '_default'
    :param verifier: A secret used for the Native App flow. It will by default be a
        freshly generated random string, known only to this
        ``GlobusNativeAppFlowManager`` instance
    :param refresh_tokens: When True, request refresh tokens in addition to access
        tokens. [Default: ``False``]
    :param prefill_named_grant: Prefill the named grant label on the consent page
    """

    def __init__(
        self,
        auth_client: globus_sdk.NativeAppAuthClient,
        requested_scopes: ScopeCollectionType,
        redirect_uri: str | MissingType = MISSING,
        state: str = "_default",
        verifier: str | MissingType = MISSING,
        refresh_tokens: bool = False,
        prefill_named_grant: str | MissingType = MISSING,
    ) -> None:
        self.auth_client = auth_client

        # set client_id, then check for validity
        self.client_id = auth_client.client_id
        if not self.client_id:
            log.error(
                "Invalid auth_client ID to start Native App Flow: {}".format(
                    self.client_id
                )
            )
            raise GlobusSDKUsageError(
                f'Invalid value for client_id. Got "{self.client_id}"'
            )

        # convert scopes iterable to string immediately on load
        self.requested_scopes = stringify_requested_scopes(requested_scopes)

        # default to `/v2/web/auth-code` on whatever environment we're looking
        # at -- most typically it will be `https://auth.globus.org/`
        self.redirect_uri = redirect_uri or (
            slash_join(auth_client.base_url, "/v2/web/auth-code")
        )

        # make a challenge and secret to keep
        # if the verifier is provided, it will just be passed back to us, and
        # if not, one will be generated
        self.verifier, self.challenge = _make_native_app_challenge(verifier)

        # store the remaining parameters directly, with no transformation
        self.refresh_tokens = refresh_tokens
        self.state = state
        self.prefill_named_grant = prefill_named_grant

        log.debug(
            "Starting Native App Flow with params: "
            f"auth_client.client_id={auth_client.client_id} , "
            f"redirect_uri={self.redirect_uri} , "
            f"refresh_tokens={refresh_tokens} , "
            f"state={state} , "
            f"requested_scopes={self.requested_scopes} , "
            f"verifier=<REDACTED>,challenge={self.challenge}"
        )

        if prefill_named_grant is not MISSING:
            log.debug(f"prefill_named_grant={self.prefill_named_grant}")

    def get_authorize_url(self, query_params: dict[str, t.Any] | None = None) -> str:
        """
        Start a Native App flow by getting the authorization URL to which users
        should be sent.

        :param query_params: Additional query parameters to include in the
            authorize URL. Primarily for internal use

        The returned URL string is encoded to be suitable to display to users
        in a link or to copy into their browser. Users will be redirected
        either to your provided ``redirect_uri`` or to the default location,
        with the ``auth_code`` embedded in a query parameter.
        """
        authorize_base_url = slash_join(
            self.auth_client.base_url, "/v2/oauth2/authorize"
        )
        log.debug(f"Building authorization URI. Base URL: {authorize_base_url}")
        log.debug(f"query_params={query_params}")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.requested_scopes,
            "state": self.state,
            "response_type": "code",
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "access_type": (self.refresh_tokens and "offline") or "online",
            "prefill_named_grant": self.prefill_named_grant,
            **(query_params or {}),
        }
        params = filter_missing(params)

        encoded_params = urllib.parse.urlencode(params)
        return f"{authorize_base_url}?{encoded_params}"

    def exchange_code_for_tokens(
        self, auth_code: str
    ) -> OAuthAuthorizationCodeResponse:
        """
        The second step of the Native App flow, exchange an authorization code
        for access tokens (and refresh tokens if specified).

        :param auth_code: The short-lived code to exchange for tokens
        """
        log.debug(
            "Performing Native App auth_code exchange. "
            "Sending verifier and client_id"
        )
        return self.auth_client.oauth2_token(
            {
                "client_id": self.client_id,
                "grant_type": "authorization_code",
                "code": auth_code.encode("utf-8"),
                "code_verifier": self.verifier,
                "redirect_uri": self.redirect_uri,
            },
            response_class=OAuthAuthorizationCodeResponse,
        )
