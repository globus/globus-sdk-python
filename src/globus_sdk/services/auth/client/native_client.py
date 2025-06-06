from __future__ import annotations

import logging
import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.response import GlobusHTTPResponse

from ..flow_managers import GlobusNativeAppFlowManager
from ..response import OAuthRefreshTokenResponse
from .base_login_client import AuthLoginClient

log = logging.getLogger(__name__)


class NativeAppAuthClient(AuthLoginClient):
    """
    This type of ``AuthLoginClient`` is used to represent a Native App's
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

    def __init__(
        self,
        client_id: UUIDLike,
        environment: str | None = None,
        base_url: str | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            client_id=client_id,
            authorizer=NullAuthorizer(),
            environment=environment,
            base_url=base_url,
            app_name=app_name,
            transport_params=transport_params,
        )

    def oauth2_start_flow(
        self,
        requested_scopes: ScopeCollectionType,
        *,
        redirect_uri: str | MissingType = MISSING,
        state: str = "_default",
        verifier: str | MissingType = MISSING,
        refresh_tokens: bool = False,
        prefill_named_grant: str | MissingType = MISSING,
    ) -> GlobusNativeAppFlowManager:
        """
        Starts a Native App OAuth2 flow.

        This is done internally by instantiating a
        :class:`GlobusNativeAppFlowManager <.GlobusNativeAppFlowManager>`

        While the flow is in progress, the ``NativeAppAuthClient`` becomes
        non thread-safe as temporary state is stored during the flow.

        :param requested_scopes: The scopes on the token(s) being requested. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
        :param redirect_uri: The page that users should be directed to after
            authenticating at the authorize URL. Defaults to
            'https://auth.globus.org/v2/web/auth-code', which displays the resulting
            ``auth_code`` for users to copy-paste back into your application (and
            thereby be passed back to the ``GlobusNativeAppFlowManager``)
        :param state: The ``redirect_uri`` page will have this included in a query
            parameter, so you can use it to pass information to that page if you use a
            custom page. It defaults to the string '_default'
        :param verifier: A secret used for the Native App flow. It will by default be a
            freshly generated random string, known only to this
            ``GlobusNativeAppFlowManager`` instance
        :param refresh_tokens: When True, request refresh tokens in addition to access
            tokens. [Default: ``False``]
        :param prefill_named_grant: Prefill the named grant label on the consent page

        .. tab-set::

            .. tab-item:: Example Usage

                You can see an example of this flow :ref:`in the usage examples
                <examples_native_app_login>`.

            .. tab-item:: API Info

                The Globus Auth specification for Native App grants details
                modifications to the Authorization Code grant flow as
                `The PKCE Security Protocol
                <https://docs.globus.org/api/auth/developer-guide/#pkce>`_.
        """
        log.debug("Starting Native App Grant Flow")
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

    def oauth2_refresh_token(
        self,
        refresh_token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> OAuthRefreshTokenResponse:
        """
        ``NativeAppAuthClient`` specializes the refresh token grant to include
        its client ID as a parameter in the POST body.
        It needs this specialization because it cannot authenticate the refresh
        grant call with client credentials, as is normal.

        :param refresh_token: The refresh token to use to get a new access token
        :param body_params: Extra parameters to include in the POST body
        """
        log.debug("Executing token refresh without client credentials")
        form_data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.client_id,
        }
        return self.oauth2_token(
            form_data, body_params=body_params, response_class=OAuthRefreshTokenResponse
        )

    def create_native_app_instance(
        self,
        template_id: UUIDLike,
        name: str,
    ) -> GlobusHTTPResponse:
        """
         Create a new native app instance. The new instance is a confidential client.

         :param template_id: The client ID of the calling native app
         :param name: The name given to the new app instance

        .. tab-set::

             .. tab-item:: Example Usage

                 .. code-block:: pycon

                     >>> ac = globus_sdk.NativeAppAuthClient(...)
                     >>> template_id = ...
                     >>> r = ac.create_native_app_instance(
                     ...     template_id,
                     ...     "My new native app instance",
                     ... )
                     >>> client_id = r["client"]["id"]

             .. tab-item:: Example Response Data

                 .. expandtestfixture:: auth.create_native_app_instance

             .. tab-item:: API Info

                 ``POST /v2/api/clients``

                 .. extdoclink:: Create Client
                     :ref: auth/reference/#create_client
        """
        body: dict[str, t.Any] = {
            "name": name,
            "template_id": template_id,
        }
        return self.post("/v2/api/clients", data={"client": body})
