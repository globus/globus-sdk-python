from __future__ import annotations

import collections.abc
import json
import logging
import sys
import typing as t

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import _guards
from globus_sdk.authorizers import GlobusAuthorizer

if sys.version_info >= (3, 8):
    # pylint can't handle quoted annotations yet:
    # https://github.com/PyCQA/pylint/issues/3299
    from typing import Literal  # pylint: disable=unused-import
else:
    from typing_extensions import Literal

from globus_sdk import client, exc, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.response import GlobusHTTPResponse, IterableResponse
from globus_sdk.scopes import AuthScopes

from ..errors import AuthAPIError
from ..flow_managers import GlobusOAuthFlowManager
from ..response import (
    GetIdentitiesResponse,
    GetIdentityProvidersResponse,
    GetProjectsResponse,
    OAuthTokenResponse,
)

log = logging.getLogger(__name__)

RT = t.TypeVar("RT", bound=GlobusHTTPResponse)


class AuthClient(client.BaseClient):
    """
    Client for the
    `Globus Auth API <https://docs.globus.org/api/auth/>`_

    This class provides helper methods for most common resources in the
    Auth API, and the common low-level interface from
    :class:`BaseClient <globus_sdk.client.BaseClient>` of ``get``, ``put``,
    ``post``, and ``delete`` methods, which can be used to access any API
    resource.

    There are generally two types of resources, distinguished by the type
    of authentication which they use. Resources available to end users of
    Globus are authenticated with a Globus Auth Token
    ("Authentication: Bearer ..."), while resources available to OAuth
    Clients are authenticated using Basic Auth with the Client's ID and
    Secret.
    Some resources may be available with either authentication type.

    **Examples**

    Initializing an ``AuthClient`` to authenticate a user making calls to the
    Globus Auth service with an access token takes the form

    >>> from globus_sdk import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))

    You can, of course, use other kinds of Authorizers (notably the
    ``RefreshTokenAuthorizer``).

    .. automethodlist:: globus_sdk.AuthClient
    """

    service_name = "auth"
    error_class = AuthAPIError
    scopes = AuthScopes

    def __init__(
        self,
        client_id: UUIDLike | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            environment=environment,
            base_url=base_url,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )
        self.client_id: str | None = str(client_id) if client_id is not None else None
        # an AuthClient may contain a GlobusOAuth2FlowManager in order to
        # encapsulate the functionality of various different types of flow
        # managers
        self.current_oauth2_flow_manager: GlobusOAuthFlowManager | None = None

        log.info(
            "Finished initializing AuthClient. "
            f"client_id='{client_id}', type(authorizer)={type(authorizer)}"
        )

    def get_identities(
        self,
        *,
        usernames: t.Iterable[str] | str | None = None,
        ids: t.Iterable[UUIDLike] | UUIDLike | None = None,
        provision: bool = False,
        query_params: dict[str, t.Any] | None = None,
    ) -> GetIdentitiesResponse:
        r"""
        Given ``usernames=<U>`` or (exclusive) ``ids=<I>`` as keyword
        arguments, looks up identity information for the set of identities
        provided.
        ``<U>`` and ``<I>`` in this case are comma-delimited strings listing
        multiple Identity Usernames or Identity IDs, or iterables of strings,
        each of which is an Identity Username or Identity ID.

        If Globus Auth's identity auto-provisioning behavior is desired,
        ``provision=True`` may be specified.

        Available with any authentication/client type.

        :param usernames: A username or list of usernames to lookup. Mutually exclusive
            with ``ids``
        :type usernames: str or iterable of str, optional
        :param ids: An identity ID or list of IDs to lookup. Mutually exclusive
            with ``usernames``
        :type ids: str, UUID, or iterable of str or UUID, optional
        :param provision: Create identities if they do not exist, allowing clients to
            get username-to-identity mappings prior to the identity being used
        :type provision: bool
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get by ID
                    >>> r = ac.get_identities(ids="46bd0f56-e24f-11e5-a510-131bef46955c")
                    >>> r.data
                    {
                      'identities': [
                        {
                          'email': None,
                          'id': '46bd0f56-e24f-11e5-a510-131bef46955c',
                          'identity_provider': '7daddf46-70c5-45ee-9f0f-7244fe7c8707',
                          'name': None,
                          'organization': None,
                          'status': 'unused',
                          'username': 'globus@globus.org'
                        }
                      ]
                    }
                    >>> ac.get_identities(
                    ...     ids=",".join(
                    ...         ("46bd0f56-e24f-11e5-a510-131bef46955c", "168edc3d-c6ba-478c-9cf8-541ff5ebdc1c")
                    ...     )
                    ... )
                    >>> # or by usernames
                    >>> ac.get_identities(usernames="globus@globus.org")
                    >>> ac.get_identities(usernames="globus@globus.org,auth@globus.org")

                You could also use iterables:

                .. code-block:: python

                    ac.get_identities(usernames=["globus@globus.org", "auth@globus.org"])

                    ac.get_identities(
                        ids=["46bd0f56-e24f-11e5-a510-131bef46955c", "168edc3d-c6ba-478c-9cf8-541ff5ebdc1c"]
                    )

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for identity in ac.get_identities(usernames=["globus@globus.org", "auth@globus.org"]):
                        print(identity["id"])

            .. tab-item:: API Info

                ``GET /v2/api/identities``

                .. extdoclink:: Get Identities
                    :ref: auth/reference/#v2_api_identities_resources
        """  # noqa: E501

        log.info("Looking up Globus Auth Identities")

        if query_params is None:
            query_params = {}

        # if either of these params has a truthy value, stringify it
        if usernames:
            query_params["usernames"] = _commasep(usernames)
            query_params["provision"] = (
                "false" if str(provision).lower() == "false" else "true"
            )
        if ids:
            query_params["ids"] = _commasep(ids)

        log.debug(f"query_params={query_params}")

        if "usernames" in query_params and "ids" in query_params:
            log.warning(
                "get_identities call with both usernames and "
                "identities set! Expected to result in errors"
            )

        return GetIdentitiesResponse(
            self.get("/v2/api/identities", query_params=query_params)
        )

    def get_identity_providers(
        self,
        *,
        domains: t.Iterable[str] | str | None = None,
        ids: t.Iterable[UUIDLike] | UUIDLike | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> GetIdentityProvidersResponse:
        r"""
        Look up information about identity providers by domains or by IDs.

        :param domains: A domain or iterable of domains to lookup. Mutually exclusive
            with ``ids``.
        :type domains: str or iterable of str, optional
        :param ids: An identity provider ID or iterable of IDs to lookup. Mutually exclusive
            with ``domains``.
        :type ids: str, UUID, or iterable of str or UUID, optional
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get by ID
                    >>> r = ac.get_identity_providers(ids="41143743-f3c8-4d60-bbdb-eeecaba85bd9")
                    >>> r.data
                    {
                      "identity_providers": [
                        {
                          "alternative_names": [],
                          "name": "Globus ID",
                          "domains": ["globusid.org"],
                          "id": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
                          "short_name": "globusid"
                        }
                      ]
                    }
                    >>> ac.get_identities(
                    ...     ids=["41143743-f3c8-4d60-bbdb-eeecaba85bd9", "927d7238-f917-4eb2-9ace-c523fa9ba34e"]
                    ... )
                    >>> # or by domain
                    >>> ac.get_identities(domains="globusid.org")
                    >>> ac.get_identities(domains=["globus.org", "globusid.org"])

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for idp in ac.get_identity_providers(domains=["globus.org", "globusid.org"]):
                        print(f"name: {idp['name']}")
                        print(f"id: {idp['id']}")
                        print(f"domains: {idp['domains']}")
                        print()

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_identity_providers

            .. tab-item:: API Info

                ``GET /v2/api/identity_providers``

                .. extdoclink:: Get Identity Providers
                    :ref: auth/reference/#get_identity_providers
        """  # noqa: E501

        log.info("Looking up Globus Auth Identity Providers")

        if query_params is None:
            query_params = {}

        if domains is not None and ids is not None:
            raise exc.GlobusSDKUsageError(
                "AuthClient.get_identity_providers does not take both "
                "'domains' and 'ids'. These are mutually exclusive."
            )
        # if either of these params has a truthy value, stringify it
        # this handles lists of values as well as individual values gracefully
        # letting us consume args whose `__str__` methods produce "the right
        # thing"
        elif domains is not None:
            query_params["domains"] = _commasep(domains)
        elif ids is not None:
            query_params["ids"] = _commasep(ids)
        else:
            log.warning(
                "neither 'domains' nor 'ids' provided to get_identity_providers(). "
                "This can only succeed if 'query_params' were given."
            )

        log.debug(f"query_params={query_params}")
        return GetIdentityProvidersResponse(
            self.get("/v2/api/identity_providers", query_params=query_params)
        )

    #
    # Developer APIs
    #

    def get_projects(self) -> IterableResponse:
        """
        Look up projects on which the authenticated user is an admin.
        Requires the ``manage_projects`` scope.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_projects()
                    >>> r.data
                    {
                      'projects": [
                        {
                          'admin_ids": ["41143743-f3c8-4d60-bbdb-eeecaba85bd9"]
                          'contact_email": "support@globus.org",
                          'display_name": "Globus SDK Demo Project",
                          'admin_group_ids": None,
                          'id": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
                          'project_name": "Globus SDK Demo Project",
                          'admins": {
                            'identities": ["41143743-f3c8-4d60-bbdb-eeecaba85bd9"],
                            'groups": [],
                          },
                      ]
                    }

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for project in ac.get_projects():
                        print(f"name: {project['display_name']}")
                        print(f"id: {project['id']}")
                        print()

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_projects

            .. tab-item:: API Info

                ``GET /v2/api/projects``

                .. extdoclink:: Get Projects
                    :ref: auth/reference/#get_projects
        """  # noqa: E501
        return GetProjectsResponse(self.get("/v2/api/projects"))

    def create_project(
        self,
        display_name: str,
        contact_email: str,
        *,
        admin_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
        admin_group_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Create a new project. Requires the ``manage_projects`` scope.

        At least one of ``admin_ids`` or ``admin_group_ids`` must be provided.

        :param display_name: The name of the project
        :type display_name: str
        :param contact_email: The email address of the project's point of contact
        :type contact_email: str
        :param admin_ids: A list of user IDs to be added as admins of the project
        :type admin_ids: str or uuid or iterable of str or uuid, optional
        :param admin_group_ids: A list of group IDs to be added as admins of the project
        :type admin_group_ids: str or uuid or iterable of str or uuid, optional

        .. tab-set::

            .. tab-item:: Example Usage

                When creating a project, your account is not necessarily included as an
                admin. The following snippet uses the ``manage_projects`` scope as well
                as the ``openid`` and ``email`` scopes to get the current user ID and
                email address and use those data to setup the project.

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> userinfo = ac.oauth2_userinfo()
                    >>> identity_id = userinfo["sub"]
                    >>> email = userinfo["email"]
                    >>> r = ac.create_project(
                    ...     "My Project",
                    ...     contact_email=email,
                    ...     admin_ids=identity_id,
                    ... )
                    >>> project_id = r["project"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_project

            .. tab-item:: API Info

                ``POST /v2/api/projects``

                .. extdoclink:: Create Project
                    :ref: auth/reference/#create_project
        """
        body: dict[str, t.Any] = {
            "display_name": display_name,
            "contact_email": contact_email,
        }
        if admin_ids is not None:
            body["admin_ids"] = list(utils.safe_strseq_iter(admin_ids))
        if admin_group_ids is not None:
            body["admin_group_ids"] = list(utils.safe_strseq_iter(admin_group_ids))
        return self.post("/v2/api/projects", data={"project": body})

    def update_project(
        self,
        project_id: UUIDLike,
        *,
        display_name: str | None = None,
        contact_email: str | None = None,
        admin_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
        admin_group_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Update a project. Requires the ``manage_projects`` scope.

        :param project_id: The ID of the project to update
        :type project_id: str or uuid
        :param display_name: The name of the project
        :type display_name: str
        :param contact_email: The email address of the project's point of contact
        :type contact_email: str
        :param admin_ids: A list of user IDs to be set as admins of the project
        :type admin_ids: str or uuid or iterable of str or uuid, optional
        :param admin_group_ids: A list of group IDs to be set as admins of the project
        :type admin_group_ids: str or uuid or iterable of str or uuid, optional

        .. tab-set::

            .. tab-item:: Example Usage

                The following snippet uses the ``manage_projects`` scope as well
                as the ``email`` scope to get the current user email address and set it
                as a project's contact email:

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> project_id = ...
                    >>> userinfo = ac.oauth2_userinfo()
                    >>> email = userinfo["email"]
                    >>> r = ac.update_project(project_id, contact_email=email)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.update_project

            .. tab-item:: API Info

                ``POST /v2/api/projects``

                .. extdoclink:: Update Project
                    :ref: auth/reference/#update_project
        """
        body: dict[str, t.Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if contact_email is not None:
            body["contact_email"] = contact_email
        if admin_ids is not None:
            body["admin_ids"] = list(utils.safe_strseq_iter(admin_ids))
        if admin_group_ids is not None:
            body["admin_group_ids"] = list(utils.safe_strseq_iter(admin_group_ids))
        return self.put(f"/v2/api/projects/{project_id}", data={"project": body})

    def delete_project(self, project_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a project. Requires the ``manage_projects`` scope.

        :param project_id: The ID of the project to delete
        :type project_id: str or uuid

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> project_id = ...
                    >>> r = ac.delete_project(project_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_project

            .. tab-item:: API Info

                ``DELETE /v2/api/projects/{project_id}``

                .. extdoclink:: Delete Project
                    :ref: auth/reference/#delete_project
        """
        return self.delete(f"/v2/api/projects/{project_id}")

    #
    # OAuth2 Behaviors & APIs
    #

    def oauth2_get_authorize_url(
        self,
        *,
        session_required_identities: UUIDLike | t.Iterable[UUIDLike] | None = None,
        session_required_single_domain: str | t.Iterable[str] | None = None,
        session_required_policies: UUIDLike | t.Iterable[UUIDLike] | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> str:
        """
        Get the authorization URL to which users should be sent.
        This method may only be called after ``oauth2_start_flow``
        has been called on this ``AuthClient``.

        :param session_required_identities: A list of identities must be
            added to the session.
        :type session_required_identities: str or uuid or list of str or uuid, optional
        :param session_required_single_domain: A list of domain requirements
            which must be satisfied by identities added to the session.
        :type session_required_single_domain: str or list of str, optional
        :param session_required_policies: A list of IDs for policies which must
            be satisfied by the user.
        :type session_required_policies: str or uuid or list of str or uuid, optional
        :param query_params: Additional query parameters to include in the
            authorize URL. Primarily for internal use
        :type query_params: dict, optional
        :rtype: ``string``
        """
        if not self.current_oauth2_flow_manager:
            log.error("OutOfOrderOperations(get_authorize_url before start_flow)")
            raise exc.GlobusSDKUsageError(
                "Cannot get authorize URL until starting an OAuth2 flow. "
                "Call the oauth2_start_flow() method on this "
                "AuthClient to resolve"
            )
        if query_params is None:
            query_params = {}
        if session_required_identities is not None:
            query_params["session_required_identities"] = _commasep(
                session_required_identities
            )
        if session_required_single_domain is not None:
            query_params["session_required_single_domain"] = _commasep(
                session_required_single_domain
            )
        if session_required_policies is not None:
            query_params["session_required_policies"] = _commasep(
                session_required_policies
            )
        auth_url = self.current_oauth2_flow_manager.get_authorize_url(
            query_params=query_params
        )
        log.info(f"Got authorization URL: {auth_url}")
        return auth_url

    def oauth2_exchange_code_for_tokens(self, auth_code: str) -> OAuthTokenResponse:
        """
        Exchange an authorization code for a token or tokens.

        :rtype: :class:`OAuthTokenResponse <.OAuthTokenResponse>`

        :param auth_code: An auth code typically obtained by sending the user to the
            authorize URL. The code is a very short-lived credential which this method
            is exchanging for tokens. Tokens are the credentials used to authenticate
            against Globus APIs.
        :type auth_code: str
        """
        log.info(
            "Final Step of 3-legged OAuth2 Flows: "
            "Exchanging authorization code for token(s)"
        )
        if not self.current_oauth2_flow_manager:
            log.error("OutOfOrderOperations(exchange_code before start_flow)")
            raise exc.GlobusSDKUsageError(
                "Cannot exchange auth code until starting an OAuth2 flow. "
                "Call the oauth2_start_flow() method on this "
                "AuthClient to resolve"
            )

        return self.current_oauth2_flow_manager.exchange_code_for_tokens(auth_code)

    def oauth2_refresh_token(
        self,
        refresh_token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> OAuthTokenResponse:
        r"""
        Exchange a refresh token for a
        :class:`OAuthTokenResponse <.OAuthTokenResponse>`, containing
        an access token.

        Does a token call of the form

        .. code-block:: none

            refresh_token=<refresh_token>
            grant_type=refresh_token

        plus any additional parameters you may specify.

        :param refresh_token: A Globus Refresh Token as a string
        :type refresh_token: str

        :param body_params: A dict of extra params to encode in the refresh call.
        :type body_params: dict, optional
        """
        log.info("Executing token refresh; typically requires client credentials")
        form_data = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
        return self.oauth2_token(form_data, body_params=body_params)

    def oauth2_validate_token(
        self,
        token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Validate a token. It can be an Access Token or a Refresh token.

        This call can be used to check tokens issued to your client,
        confirming that they are or are not still valid. The resulting response
        has the form ``{"active": True}`` when the token is valid, and
        ``{"active": False}`` when it is not.

        It is not necessary to validate tokens immediately after receiving them
        from the service -- any tokens which you are issued will be valid at
        that time. This is more for the purpose of doing checks like

        - confirm that ``oauth2_revoke_token`` succeeded
        - at application boot, confirm no need to do fresh login

        :param token: The token which should be validated. Can be a refresh token or an
            access token
        :type token: str
        :param body_params: Additional parameters to include in the validation
            body. Primarily for internal use
        :type body_params: dict, optional

        **Examples**

        Revoke a token and confirm that it is no longer active:

        >>> from globus_sdk import ConfidentialAppAuthClient
        >>> ac = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
        >>> ac.oauth2_revoke_token('<token_string>')
        >>> data = ac.oauth2_validate_token('<token_string>')
        >>> assert not data['active']

        During application boot, check if the user needs to do a login, even
        if a token is present:

        >>> from globus_sdk import ConfidentialAppAuthClient
        >>> ac = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
        >>> # this is not an SDK function, but a hypothetical function which
        >>> # you use to load a token out of configuration data
        >>> tok = load_token_from_config(...)
        >>>
        >>> if not tok or not ac.oauth2_validate_token(tok)['active']:
        >>>     # do_new_login() is another hypothetical helper
        >>>     tok = do_new_login()
        >>> # at this point, tok is expected to be a valid token
        """
        log.info("Validating token")
        body = {"token": token}

        # if this client has no way of authenticating itself but
        # it does have a client_id, we'll send that in the request
        no_authentication = _guards.is_optional(self.authorizer, NullAuthorizer)
        if no_authentication and self.client_id:
            log.debug("Validating token with unauthenticated client")
            body.update({"client_id": self.client_id})

        if body_params:
            body.update(body_params)
        return self.post("/v2/oauth2/token/validate", data=body, encoding="form")

    def oauth2_revoke_token(
        self,
        token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Revoke a token. It can be an Access Token or a Refresh token.

        This call should be used to revoke tokens issued to your client,
        rendering them inert and not further usable. Typically, this is
        incorporated into "logout" functionality, but it should also be used if
        the client detects that its tokens are in an unsafe location (e.x.
        found in a world-readable logfile).

        You can check the "active" status of the token after revocation if you
        want to confirm that it was revoked.

        :param token: The token which should be revoked
        :type token: str
        :param body_params: Additional parameters to include in the revocation
            body, which can help speed the revocation process. Primarily for
            internal use
        :type body_params: dict, optional

        **Examples**

        >>> from globus_sdk import ConfidentialAppAuthClient
        >>> ac = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
        >>> ac.oauth2_revoke_token('<token_string>')
        """
        log.info("Revoking token")
        body = {"token": token}

        # if this client has no way of authenticating itself but
        # it does have a client_id, we'll send that in the request
        no_authentication = self.authorizer is None or isinstance(
            self.authorizer, NullAuthorizer
        )
        if no_authentication and self.client_id:
            log.debug("Revoking token with unauthenticated client")
            body.update({"client_id": self.client_id})

        if body_params:
            body.update(body_params)
        return self.post("/v2/oauth2/token/revoke", data=body, encoding="form")

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
    ) -> OAuthTokenResponse:
        ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None,
    ) -> OAuthTokenResponse:
        ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        response_class: type[RT],
    ) -> RT:
        ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None,
        response_class: type[RT],
    ) -> RT:
        ...

    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None = None,
        response_class: (type[OAuthTokenResponse] | type[RT]) = OAuthTokenResponse,
    ) -> OAuthTokenResponse | RT:
        """
        This is the generic form of calling the OAuth2 Token endpoint.
        It takes ``form_data``, a dict which will be encoded in a form POST
        body on the request.

        Generally, users of the SDK should not call this method unless they are
        implementing OAuth2 flows.

        :param response_class: This is used by calls to the oauth2_token endpoint which
            need to specialize their responses. For example,
            :meth:`oauth2_get_dependent_tokens \
            <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
            requires a specialize response class to handle the dramatically different
            format of the Dependent Token Grant response
        :type response_class: class, optional
        :param form_data: The main body of the request
        :type form_data: dict or `utils.PayloadWrapper`
        :param body_params: Any additional parameters to be passed through
            as body parameters.
        :type body_params: dict, optional
        :rtype: ``response_class``
        """
        log.info("Fetching new token from Globus Auth")
        # use the fact that requests implicitly encodes the `data` parameter as
        # a form POST
        data = dict(form_data)
        if body_params:
            data.update(body_params)
        return response_class(
            self.post(
                "/v2/oauth2/token",
                data=data,
                encoding="form",
            )
        )

    def oauth2_userinfo(self) -> GlobusHTTPResponse:
        """
        Call the Userinfo endpoint of Globus Auth.
        Userinfo is specified as part of the OpenID Connect (OIDC) standard,
        and Globus Auth's Userinfo is OIDC-compliant.

        The exact data returned will depend upon the set of OIDC-related scopes
        which were used to acquire the token being used for this call. For
        details, see the **API Info** below.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    ac = AuthClient(...)
                    info = ac.oauth2_userinfo()
                    print(
                        'Effective Identity "{info["sub"]}" has '
                        f'Full Name "{info["name"]}" and '
                        f'Email "{info["email"]}"'
                    )

            .. tab-item:: API Info

                ``GET /v2/oauth2/userinfo``

                .. extdoclink:: Get Userinfo
                    :ref: auth/reference/#get_or_post_v2_oauth2_userinfo_resource
        """
        log.info("Looking up OIDC-style Userinfo from Globus Auth")
        return self.get("/v2/oauth2/userinfo")

    def get_openid_configuration(self) -> GlobusHTTPResponse:
        """
        Fetch the OpenID Connect configuration data from the well-known URI for Globus
        Auth.
        """
        log.info("Fetching OIDC Config")
        return self.get("/.well-known/openid-configuration")

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]),
        *,
        as_pem: Literal[True],
    ) -> RSAPublicKey:
        ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]),
        *,
        as_pem: Literal[False],
    ) -> dict[str, t.Any]:
        ...

    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]) = None,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]:
        """
        Fetch the Globus Auth JWK.

        Returns either a dict or an RSA Public Key object depending on ``as_pem``.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :type openid_configuration: dict or GlobusHTTPResponse
        :param as_pem: Decode the JWK to an RSA PEM key, typically for JWT decoding
        :type as_pem: bool
        """
        log.info("Fetching JWK")
        if openid_configuration:
            jwks_uri = openid_configuration["jwks_uri"]
        else:
            log.debug("No OIDC Config provided, autofetching...")
            jwks_uri = self.get_openid_configuration()["jwks_uri"]

        log.debug("jwks_uri=%s", jwks_uri)
        jwk_data = self.get(jwks_uri).data
        if not as_pem:
            log.debug("returning jwk data where as_pem=False")
            return dict(jwk_data)
        else:
            log.debug("JWK as_pem=True requested, decoding...")
            # decode from JWK to an RSA PEM key for JWT decoding
            # cast here because this should never be private key
            jwk_as_pem: RSAPublicKey = t.cast(
                RSAPublicKey,
                jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk_data["keys"][0])),
            )
            log.debug("JWK PEM decoding finished successfully")
            return jwk_as_pem


def _commasep(val: UUIDLike | t.Iterable[UUIDLike]) -> str:
    # note that this explicit handling of Iterable allows for string-like objects to be
    # passed to this function and be stringified by the `str()` call
    if isinstance(val, collections.abc.Iterable):
        return ",".join(utils.safe_strseq_iter(val))
    return str(val)
