import base64
import hashlib
import logging
import os
import re
import urllib.parse
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from globus_sdk import utils
from globus_sdk.exc import GlobusSDKUsageError

from .client_types.base import AuthClient
from .oauth2_constants import DEFAULT_REQUESTED_SCOPES
from .oauth2_flow_manager import GlobusOAuthFlowManager
from .token_response import OAuthTokenResponse

logger = logging.getLogger(__name__)


def make_native_app_challenge(verifier: Optional[str] = None) -> Tuple[str, str]:
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
    :type verifier: str, optional
    """

    if verifier:
        if not 43 <= len(verifier) <= 128:
            raise GlobusSDKUsageError(
                f"verifier must be 43-128 characters long: {len(verifier)}"
            )
        if bool(re.search(r"[^a-zA-Z0-9~_.-]", verifier)):
            raise GlobusSDKUsageError("verifier contained invalid characters")
    else:
        logger.info(
            "Autogenerating verifier secret. On low-entropy systems "
            "this may be insecure"
        )

    code_verifier = verifier or base64.urlsafe_b64encode(os.urandom(32)).decode(
        "utf-8"
    ).rstrip("=")
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

    :param auth_client: The ``NativeAppAuthClient`` object on which this flow is based.
        It is used to extract default values for the flow, and also to make calls to the
        Auth service.
    :type auth_client: :class:`NativeAppAuthClient <globus_sdk.NativeAppAuthClient>`
    :param requested_scopes: The scopes on the token(s) being requested, as a
        space-separated string or iterable of strings. Defaults to
        ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
    :type requested_scopes: str or iterable of str, optional
    :param redirect_uri: The page that users should be directed to after authenticating
        at the authorize URL. Defaults to 'https://auth.globus.org/v2/web/auth-code',
        which displays the resulting ``auth_code`` for users to copy-paste back into
        your application (and thereby be passed back to the
        ``GlobusNativeAppFlowManager``)
    :type redirect_uri: str, optional
    :param state: The ``redirect_uri`` page will have this included in a query
        parameter, so you can use it to pass information to that page if you use a
        custom page. It defaults to the string '_default'
    :type state: str, optional
    :param verifier: A secret used for the Native App flow. It will by default be a
        freshly generated random string, known only to this
        ``GlobusNativeAppFlowManager`` instance
    :type verifier: str, optional
    :param refresh_tokens: When True, request refresh tokens in addition to access
        tokens. [Default: ``False``]
    :type refresh_tokens: bool, optional
    :param prefill_named_grant: Prefill the named grant label on the consent page
    :type prefill_named_grant: str, optional
    """

    def __init__(
        self,
        auth_client: AuthClient,
        requested_scopes: Optional[Union[str, Sequence[str]]] = None,
        redirect_uri: Optional[str] = None,
        state: str = "_default",
        verifier: Optional[str] = None,
        refresh_tokens: bool = False,
        prefill_named_grant: Optional[str] = None,
    ):
        self.auth_client = auth_client

        # set client_id, then check for validity
        self.client_id = auth_client.client_id
        if not self.client_id:
            logger.error(
                "Invalid auth_client ID to start Native App Flow: {}".format(
                    self.client_id
                )
            )
            raise GlobusSDKUsageError(
                f'Invalid value for client_id. Got "{self.client_id}"'
            )

        # default to the default requested scopes
        self.requested_scopes = requested_scopes or DEFAULT_REQUESTED_SCOPES
        # convert scopes iterable to string immediately on load
        if not isinstance(self.requested_scopes, str):
            self.requested_scopes = " ".join(self.requested_scopes)

        # default to `/v2/web/auth-code` on whatever environment we're looking
        # at -- most typically it will be `https://auth.globus.org/`
        self.redirect_uri = redirect_uri or (
            utils.slash_join(auth_client.base_url, "/v2/web/auth-code")
        )

        # make a challenge and secret to keep
        # if the verifier is provided, it will just be passed back to us, and
        # if not, one will be generated
        self.verifier, self.challenge = make_native_app_challenge(verifier)

        # store the remaining parameters directly, with no transformation
        self.refresh_tokens = refresh_tokens
        self.state = state
        self.prefill_named_grant = prefill_named_grant

        logger.debug("Starting Native App Flow with params:")
        logger.debug(f"auth_client.client_id={auth_client.client_id}")
        logger.debug(f"redirect_uri={self.redirect_uri}")
        logger.debug(f"refresh_tokens={refresh_tokens}")
        logger.debug(f"state={state}")
        logger.debug(f"requested_scopes={self.requested_scopes}")
        logger.debug(f"verifier=<REDACTED>,challenge={self.challenge}")

        if prefill_named_grant is not None:
            logger.debug(f"prefill_named_grant={self.prefill_named_grant}")

    def get_authorize_url(
        self, additional_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a Native App flow by getting the authorization URL to which users
        should be sent.

        :param additional_params: Additional query parameters to include in the
            authorize URL. Primarily for internal use
        :type additional_params: dict, optional
        :rtype: ``string``

        The returned URL string is encoded to be suitable to display to users
        in a link or to copy into their browser. Users will be redirected
        either to your provided ``redirect_uri`` or to the default location,
        with the ``auth_code`` embedded in a query parameter.
        """
        authorize_base_url = utils.slash_join(
            self.auth_client.base_url, "/v2/oauth2/authorize"
        )
        logger.debug(f"Building authorization URI. Base URL: {authorize_base_url}")
        logger.debug(f"additional_params={additional_params}")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.requested_scopes,
            "state": self.state,
            "response_type": "code",
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "access_type": (self.refresh_tokens and "offline") or "online",
        }
        if self.prefill_named_grant is not None:
            params["prefill_named_grant"] = self.prefill_named_grant
        if additional_params:
            params.update(additional_params)

        encoded_params = urllib.parse.urlencode(params)
        return f"{authorize_base_url}?{encoded_params}"

    def exchange_code_for_tokens(self, auth_code: str) -> OAuthTokenResponse:
        """
        The second step of the Native App flow, exchange an authorization code
        for access tokens (and refresh tokens if specified).

        :rtype: :class:`OAuthTokenResponse <.OAuthTokenResponse>`
        """
        logger.debug(
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
            }
        )
