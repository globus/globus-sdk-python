from __future__ import annotations

import logging
import typing as t

from globus_sdk import exc, utils
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import BasicAuthorizer
from globus_sdk.response import GlobusHTTPResponse

from .._common import stringify_requested_scopes
from ..flow_managers import GlobusAuthorizationCodeFlowManager
from ..response import (
    GetIdentitiesResponse,
    OAuthDependentTokenResponse,
    OAuthTokenResponse,
)
from .base_login_client import AuthLoginClient

log = logging.getLogger(__name__)


class ConfidentialAppAuthClient(AuthLoginClient):
    """
    This is a specialized type of ``AuthLoginClient`` used to represent an App with
    a Client ID and Client Secret wishing to communicate with Globus Auth.
    It must be given a Client ID and a Client Secret, and furthermore, these
    will be used to establish a :class:`BasicAuthorizer <globus_sdk.BasicAuthorizer>`
    for authorization purposes.
    Additionally, the Client ID is stored for use in various calls.

    Confidential Applications are those which have their own credentials for
    authenticating against Globus Auth.

    :param client_id: The ID of the application provided by registration with
        Globus Auth.
    :param client_secret: The secret string to use for authentication. Secrets can be
        generated via the Globus developers interface.

    All other initialization parameters are passed through to ``BaseClient``.

    .. automethodlist:: globus_sdk.ConfidentialAppAuthClient
    """

    def __init__(
        self,
        client_id: UUIDLike,
        client_secret: str,
        environment: str | None = None,
        base_url: str | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            client_id=client_id,
            authorizer=BasicAuthorizer(str(client_id), client_secret),
            environment=environment,
            base_url=base_url,
            app_name=app_name,
            transport_params=transport_params,
        )

    def get_identities(
        self,
        *,
        usernames: t.Iterable[str] | str | None = None,
        ids: t.Iterable[UUIDLike] | UUIDLike | None = None,
        provision: bool = False,
        query_params: dict[str, t.Any] | None = None,
    ) -> GetIdentitiesResponse:
        """
        Perform a call to the Get Identities API using the direct client
        credentials of this client.

        This method is considered deprecated -- callers should instead use client
        credentials to get a token and then use that token to call the API via a
        :class:`~.AuthClient`.

        :param usernames: A username or list of usernames to lookup. Mutually exclusive
            with ``ids``
        :param ids: An identity ID or list of IDs to lookup. Mutually exclusive
            with ``usernames``
        :param provision: Create identities if they do not exist, allowing clients to
            get username-to-identity mappings prior to the identity being used
        :param query_params: Any additional parameters to be passed through
            as query params.
        """
        exc.warn_deprecated(
            "ConfidentialAuthClient.get_identities() is deprecated. "
            "Get a token via `oauth2_client_credentials_tokens` "
            "and use that to call the API instead."
        )

        if query_params is None:
            query_params = {}

        if usernames is not None:
            query_params["usernames"] = utils.commajoin(usernames)
            query_params["provision"] = (
                "false" if str(provision).lower() == "false" else "true"
            )
        if ids is not None:
            query_params["ids"] = utils.commajoin(ids)

        return GetIdentitiesResponse(
            self.get("/v2/api/identities", query_params=query_params)
        )

    def oauth2_client_credentials_tokens(
        self,
        requested_scopes: ScopeCollectionType | None = None,
    ) -> OAuthTokenResponse:
        r"""
        Perform an OAuth2 Client Credentials Grant to get access tokens which
        directly represent your client and allow it to act on its own
        (independent of any user authorization).
        This method does not use a ``GlobusOAuthFlowManager`` because it is not
        at all necessary to do so.

        :param requested_scopes: The scopes on the token(s) being requested. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``

        For example, with a Client ID of "CID1001" and a Client Secret of
        "RAND2002", you could use this grant type like so:

        >>> client = ConfidentialAppAuthClient("CID1001", "RAND2002")
        >>> tokens = client.oauth2_client_credentials_tokens()
        >>> transfer_token_info = (
        ...     tokens.by_resource_server["transfer.api.globus.org"])
        >>> transfer_token = transfer_token_info["access_token"]
        """
        log.info("Fetching token(s) using client credentials")
        requested_scopes_string = stringify_requested_scopes(requested_scopes)
        return self.oauth2_token(
            {"grant_type": "client_credentials", "scope": requested_scopes_string}
        )

    def oauth2_start_flow(
        self,
        redirect_uri: str,
        requested_scopes: ScopeCollectionType | None = None,
        *,
        state: str = "_default",
        refresh_tokens: bool = False,
    ) -> GlobusAuthorizationCodeFlowManager:
        """
        Starts or resumes an Authorization Code OAuth2 flow.

        Under the hood, this is done by instantiating a
        :class:`GlobusAuthorizationCodeFlowManager
        <.GlobusAuthorizationCodeFlowManager>`

        :param redirect_uri: The page that users should be directed to after
            authenticating at the authorize URL.
        :param requested_scopes: The scopes on the token(s) being requested. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
        :param state: This string allows an application to pass information back to
            itself in the course of the OAuth flow. Because the user will navigate away
            from the application to complete the flow, this parameter lets the app pass
            an arbitrary string from the starting page to the ``redirect_uri``
        :param refresh_tokens: When True, request refresh tokens in addition to access
            tokens. [Default: ``False``]

        .. tab-set::

            .. tab-item:: Example Usage

                You can see an example of this flow :ref:`in the usage examples
                <examples_three_legged_oauth_login>`.

            .. tab-item:: API Info

                The Authorization Code Grant flow is described
                `in the Globus Auth Specification
                <https://docs.globus.org/api/auth/developer-guide/#obtaining-authorization>`_.
        """
        log.info("Starting OAuth2 Authorization Code Grant Flow")
        self.current_oauth2_flow_manager = GlobusAuthorizationCodeFlowManager(
            self,
            redirect_uri,
            requested_scopes=requested_scopes,
            state=state,
            refresh_tokens=refresh_tokens,
        )
        return self.current_oauth2_flow_manager

    def oauth2_get_dependent_tokens(
        self,
        token: str,
        *,
        refresh_tokens: bool = False,
        scope: str | t.Iterable[str] | utils.MissingType = utils.MISSING,
        additional_params: dict[str, t.Any] | None = None,
    ) -> OAuthDependentTokenResponse:
        """
        Fetch Dependent Tokens from Globus Auth.

        This exchanges a token given to this client for a new set of tokens
        which give it access to resource servers on which it depends.
        This grant type is intended for use by Resource Servers playing out the
        following scenario:

          1. User has tokens for Service A, but Service A requires access to
             Service B on behalf of the user
          2. Service B should not see tokens scoped for Service A
          3. Service A therefore requests tokens scoped only for Service B,
             based on tokens which were originally scoped for Service A...

        In order to do this exchange, the tokens for Service A must have scopes
        which depend on scopes for Service B (the services' scopes must encode
        their relationship). As long as that is the case, Service A can use
        this Grant to get those "Dependent" or "Downstream" tokens for Service B.

        :param token: An access token as a string
        :param refresh_tokens: When True, request dependent refresh tokens in addition
            to access tokens. [Default: ``False``]
        :param scope: The scope or scopes of the dependent tokens which are being
            requested. Applications are recommended to provide this string to ensure
            that they are receiving the tokens they expect. If omitted, all available
            dependent tokens will be returned.
        :param additional_params: Additional parameters to include in the request body

        .. tab-set::

            .. tab-item:: Example Usage

                Given a token, getting a dependent token for Globus Groups might
                look like the following:

                .. code-block:: python

                    ac = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
                    dependent_token_data = ac.oauth2_get_dependent_tokens(
                        "<token_string>",
                        scope="urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships",
                    )

                    group_token_data = dependent_token_data.by_resource_server["groups.api.globus.org"]
                    group_token = group_token_data["access_token"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.oauth2_get_dependent_tokens
                    :case: groups

            .. tab-item:: API Info

                ``POST /v2/oauth2/token``

                .. extdoclink:: Dependent Token Grant
                    :ref: auth/reference/##dependent_token_grant_post_v2oauth2token
        """  # noqa: E501
        log.info("Getting dependent tokens from access token")
        log.debug(f"additional_params={additional_params}")
        form_data = {
            "grant_type": "urn:globus:auth:grant_type:dependent_token",
            "token": token,
        }
        # the internal parameter is 'access_type', but using the name 'refresh_tokens'
        # is consistent with the rest of the SDK and better communicates expectations
        # back to the user than the OAuth2 spec wording
        if refresh_tokens:
            form_data["access_type"] = "offline"
        if not isinstance(scope, utils.MissingType):
            form_data["scope"] = " ".join(utils.safe_strseq_iter(scope))
        if additional_params:
            form_data.update(additional_params)

        return self.oauth2_token(form_data, response_class=OAuthDependentTokenResponse)

    def oauth2_token_introspect(
        self, token: str, *, include: str | None = None
    ) -> GlobusHTTPResponse:
        """
        Get information about a Globus Auth token.

        :param token: An Access Token as a raw string, being evaluated
        :param include: A value for the ``include`` parameter in the request body.
            Default is to omit the parameter.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    ac = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
                    ac.oauth2_token_introspect("<token_string>")

                Get information about a Globus Auth token including the full identity
                set of the user to whom it belongs

                .. code-block:: python

                    ac = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
                    data = ac.oauth2_token_introspect("<token_string>", include="identity_set")
                    for identity in data["identity_set"]:
                        print('token authenticates for "{}"'.format(identity))

            .. tab-item:: API Info

                ``POST /v2/oauth2/token/introspect``

                .. extdoclink:: Token Introspection
                    :ref: auth/reference/#token_introspection_post_v2_oauth2_token_introspect
        """  # noqa: E501
        log.info("Checking token validity (introspect)")
        body = {"token": token}
        if include is not None:
            body["include"] = include
        return self.post("/v2/oauth2/token/introspect", data=body, encoding="form")

    def create_child_client(
        self,
        name: str,
        *,
        public_client: bool | utils.MissingType = utils.MISSING,
        client_type: (
            t.Literal[
                "client_identity",
                "confidential_client",
                "globus_connect_server",
                "public_installed_client",
                "hybrid_confidential_client_resource_server",
                "resource_server",
            ]
            | utils.MissingType
        ) = utils.MISSING,
        visibility: t.Literal["public", "private"] | utils.MissingType = utils.MISSING,
        redirect_uris: t.Iterable[str] | utils.MissingType = utils.MISSING,
        terms_and_conditions: str | utils.MissingType = utils.MISSING,
        privacy_policy: str | utils.MissingType = utils.MISSING,
        required_idp: UUIDLike | utils.MissingType = utils.MISSING,
        preselect_idp: UUIDLike | utils.MissingType = utils.MISSING,
        additional_fields: dict[str, t.Any] | utils.MissingType = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Create a new client. Requires the ``manage_projects`` scope.

        :param name: The display name shown to users on consents. May not contain
            linebreaks.
        :param public_client: This is used to infer which OAuth grant_types the client
            will be able to use. Should be false if the client is capable of keeping
            secret credentials (such as clients running on a server) and true if it is
            not (such as native apps). After creation this value is immutable. This
            option is mutually exclusive with ``client_type``, exactly one must be
            given.
        :param client_type: Defines the type of client that will be created. This
            option is mutually exclusive with ``public_client``, exactly one must
            be given.

            .. dropdown:: Values for ``client_type``

                .. list-table::

                    * - ``"confidential_client"``
                      - Applications that are OAuth confidential clients, and can
                        manage a client secret and requests for user consent.
                    * - ``"public_installed_client"``
                      - Applications that are OAuth public clients or native
                        applications that are distributed to users, and thus cannot
                        manage a client secret.
                    * - ``"client_identity"``
                      - Applications that authenticate and act as the application
                        itself. These applications are used for automation and as
                        service or community accounts, and do NOT act on behalf of
                        other users. Also known as a "Service Account".
                    * - ``"resource_server"``
                      - An API (OAuth resource server) that uses Globus Auth tokens for
                        authentication. Users accessing the service login via Globus and
                        consent for the client to use your API.
                    * - ``"globus_connect_server"``
                      - Create a client that will service as a Globus Connect Server
                        endpoint.
                    * - ``"hybrid_confidential_client_resource_server"``
                      - A client which can use any behavior with Globus Auth - an
                        application (confidential or public client), service account,
                        or API.

        :param visibility: If set to "public", any authenticated entity can view it.
            When set to "private", only entities in the same project as the client can
            view it.
        :param redirect_uris: list of URIs that may be used in OAuth authorization
            flows.
        :param terms_and_conditions: URL of client's terms and conditions.
        :param privacy_policy: URL of client's privacy policy.
        :param required_idp: In order to use this client a user must have an identity
            from this IdP in their identity set.
        :param preselect_idp: This pre-selects the given IdP on the Globus Auth login
            page if the user is not already authenticated.
        :param additional_fields: Any additional parameters to be passed through.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> project_id = ...
                    >>> r = ac.create_child_client(
                    ...     "My client",
                    ...     True,
                    ...     True,
                    ... )
                    >>> client_id = r["client"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_child_client

            .. tab-item:: API Info

                ``POST /v2/api/clients``

                .. extdoclink:: Create Client
                    :ref: auth/reference/#create_client
        """
        # Must specify exactly one of public_client or client_type
        if public_client is not utils.MISSING and client_type is not utils.MISSING:
            raise exc.GlobusSDKUsageError(
                "AuthClient.create_client does not take both "
                "'public_client' and 'client_type'. These are mutually exclusive."
            )
        if public_client is utils.MISSING and client_type is utils.MISSING:
            raise exc.GlobusSDKUsageError(
                "AuthClient.create_client requires either 'public_client' or "
                "'client_type'."
            )

        body: dict[str, t.Any] = {
            "name": name,
            "visibility": visibility,
            "required_idp": required_idp,
            "preselect_idp": preselect_idp,
            "public_client": public_client,
            "client_type": client_type,
        }
        if not isinstance(redirect_uris, utils.MissingType):
            body["redirect_uris"] = list(utils.safe_strseq_iter(redirect_uris))

        # terms_and_conditions and privacy_policy must both be set or unset
        if bool(terms_and_conditions) ^ bool(privacy_policy):
            raise exc.GlobusSDKUsageError(
                "terms_and_conditions and privacy_policy must both be set or unset"
            )
        links: dict[str, str | utils.MissingType] = {
            "terms_and_conditions": terms_and_conditions,
            "privacy_policy": privacy_policy,
        }
        if terms_and_conditions or privacy_policy:
            body["links"] = links

        if not isinstance(additional_fields, utils.MissingType):
            body.update(additional_fields)

        return self.post("/v2/api/clients", data={"client": body})
