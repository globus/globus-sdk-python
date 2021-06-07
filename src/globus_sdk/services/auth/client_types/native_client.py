import logging

from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.exc import GlobusSDKUsageError

from ..oauth2_native_app import GlobusNativeAppFlowManager
from .base import AuthClient

log = logging.getLogger(__name__)


class NativeAppAuthClient(AuthClient):
    """
    This type of ``AuthClient`` is used to represent a Native App's
    communications with Globus Auth.
    It requires a Client ID, and cannot take an ``authorizer``.

    Native Apps are applications, like the Globus CLI, which are run
    client-side and therefore cannot keep secrets. Unable to possess client
    credentials, several Globus Auth interactions have to be specialized to
    accommodate the absence of a secret.

    Any keyword arguments given are passed through to the ``AuthClient``
    constructor.

    .. automethodlist:: globus_sdk.NativeAppAuthClient
    """

    def __init__(self, client_id, **kwargs):
        if "authorizer" in kwargs:
            log.error("ArgumentError(NativeAppClient.authorizer)")
            raise GlobusSDKUsageError("Cannot give a NativeAppAuthClient an authorizer")

        super().__init__(client_id=client_id, authorizer=NullAuthorizer(), **kwargs)
        log.info(f"Finished initializing client, client_id={client_id}")

    def oauth2_start_flow(
        self,
        requested_scopes=None,
        redirect_uri=None,
        state="_default",
        verifier=None,
        refresh_tokens=False,
        prefill_named_grant=None,
    ):
        """
        Starts a Native App OAuth2 flow.

        This is done internally by instantiating a
        :class:`GlobusNativeAppFlowManager <.GlobusNativeAppFlowManager>`

        While the flow is in progress, the ``NativeAppAuthClient`` becomes
        non thread-safe as temporary state is stored during the flow.

        :param requested_scopes: The scopes on the token(s) being requested, as a
            space-separated string or iterable of strings. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
        :type requested_scopes: str or iterable of str, optional
        :param redirect_uri: The page that users should be directed to after
            authenticating at the authorize URL. Defaults to
            'https://auth.globus.org/v2/web/auth-code', which displays the resulting
            ``auth_code`` for users to copy-paste back into your application (and
            thereby be passed back to the ``GlobusNativeAppFlowManager``)
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

        **Examples**

        You can see an example of this flow :ref:`in the usage examples
        <examples_native_app_login>`

        **External Documentation**

        The Globus Auth specification for Native App grants details the
        modifications to the Authorization Code grant flow as
        `The PKCE Security Protocol \
        <https://docs.globus.org/api/auth/developer-guide/#pkce>`_
        """
        log.info("Starting Native App Grant Flow")
        self.current_oauth2_flow_manager = GlobusNativeAppFlowManager(
            self,
            requested_scopes=requested_scopes,
            redirect_uri=redirect_uri,
            state=state,
            verifier=verifier,
            refresh_tokens=refresh_tokens,
            prefill_named_grant=prefill_named_grant,
        )
        return self.current_oauth2_flow_manager

    def oauth2_refresh_token(self, refresh_token):
        """
        ``NativeAppAuthClient`` specializes the refresh token grant to include
        its client ID as a parameter in the POST body.
        It needs this specialization because it cannot authenticate the refresh
        grant call with client credentials, as is normal.
        """
        log.info("Executing token refresh without client credentials")
        form_data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.client_id,
        }

        return self.oauth2_token(form_data)
