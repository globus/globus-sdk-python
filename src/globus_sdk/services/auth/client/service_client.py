from __future__ import annotations

import functools
import logging
import sys
import typing as t

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import client, exc, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.response import GlobusHTTPResponse, IterableResponse
from globus_sdk.scopes import AuthScopes

from .._common import get_jwk_data, pem_decode_jwk_data
from ..data import DependentScopeSpec
from ..errors import AuthAPIError
from ..response import (
    GetClientCredentialsResponse,
    GetClientsResponse,
    GetConsentsResponse,
    GetIdentitiesResponse,
    GetIdentityProvidersResponse,
    GetPoliciesResponse,
    GetProjectsResponse,
    GetScopesResponse,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

log = logging.getLogger(__name__)

F = t.TypeVar("F", bound=t.Callable[..., GlobusHTTPResponse])


def _create_policy_compat(f: F) -> F:
    @functools.wraps(f)
    def wrapper(self: t.Any, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if args:
            if len(args) > 5:
                raise TypeError(
                    "create_policy() takes 5 positional arguments "
                    f"but {len(args)} were given"
                )

            exc.warn_deprecated(
                "'AuthClient.create_policy' received positional arguments. "
                "Use only keyword arguments instead."
            )

            for argname, argvalue in zip(
                (
                    "project_id",
                    "high_assurance",
                    "authentication_assurance_timeout",
                    "display_name",
                    "description",
                ),
                args,
            ):
                if argname in kwargs:
                    raise TypeError(
                        f"create_policy() got multiple values for argument '{argname}'"
                    )
                else:
                    kwargs[argname] = argvalue

        return f(self, **kwargs)

    return t.cast(F, wrapper)


class AuthClient(client.BaseClient):
    """
    A client for using the
    `Globus Auth API <https://docs.globus.org/api/auth/>`_

    This class provides helper methods for most common resources in the
    Auth API, and the common low-level interface from
    :class:`BaseClient <globus_sdk.client.BaseClient>` of ``get``, ``put``,
    ``post``, and ``delete`` methods, which can be used to access any API
    resource.

    **Examples**

    Initializing an ``AuthClient`` to authenticate a user making calls to the
    Globus Auth service with an access token takes the form

    >>> from globus_sdk import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))

    Other authorizers, most notably ``RefreshTokenAuthorizer``, are also supported.

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

        self._client_id = str(client_id) if client_id is not None else None
        if client_id is not None:
            exc.warn_deprecated(
                "The client_id parameter is no longer accepted by `AuthClient` / "
                "`AuthClient`. When creating a client which represents an "
                "application, use `NativeAppAuthClient` or "
                "`ConfidentialAppAuthClient` instead."
            )

    # this attribute is preserved for compatibility, but will be removed in a
    # future release
    @property
    def client_id(self) -> str | None:
        exc.warn_deprecated(
            "The client_id attribute on `AuthClient` / "
            "`AuthClient` is deprecated. "
            "For clients with client IDs, use `NativeAppAuthClient` or "
            "`ConfidentialAppAuthClient` instead."
        )
        return self._client_id

    @client_id.setter
    def client_id(self, value: UUIDLike) -> None:
        exc.warn_deprecated(
            "The client_id attribute on `AuthClient` / "
            "`AuthClient` is deprecated. "
            "For clients with client IDs, use `NativeAppAuthClient` or "
            "`ConfidentialAppAuthClient` instead."
        )
        self._client_id = str(value) if value is not None else None

    # FYI: this get_openid_configuration method is duplicated in AuthLoginBaseClient
    # if this code is modified, please update that copy as well
    # this will ideally be resolved in a future SDK version by making this the only copy
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
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: Literal[True],
    ) -> RSAPublicKey: ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: Literal[False],
    ) -> dict[str, t.Any]: ...

    # FYI: this get_jwk method is duplicated in AuthLoginBaseClient
    # if this code is modified, please update that copy as well
    # this will ideally be resolved in a future SDK version by making this the only copy
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any] = None,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]:
        """
        Fetch the Globus Auth JWK.

        Returns either a dict or an RSA Public Key object depending on ``as_pem``.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :type openid_configuration: None | GlobusHTTPResponse | dict[str, typing.Any]
        :param as_pem: Decode the JWK to an RSA PEM key, typically for JWT decoding
        :type as_pem: bool
        """
        if openid_configuration is None:
            log.debug("No OIDC Config provided, autofetching...")
            openid_configuration = self.get_openid_configuration()
        jwk_data = get_jwk_data(
            fget=self.get, openid_configuration=openid_configuration
        )
        return pem_decode_jwk_data(jwk_data=jwk_data) if as_pem else jwk_data

    def userinfo(self) -> GlobusHTTPResponse:
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

    def oauth2_userinfo(self) -> GlobusHTTPResponse:
        """
        A deprecated alias for ``userinfo``.
        """
        exc.warn_deprecated(
            "The method `oauth2_userinfo` is deprecated. Use `userinfo` instead."
        )
        return self.userinfo()

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
        :param ids: An identity ID or list of IDs to lookup. Mutually exclusive
            with ``usernames``
        :param provision: Create identities if they do not exist, allowing clients to
            get username-to-identity mappings prior to the identity being used
        :param query_params: Any additional parameters to be passed through
            as query params.

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
            query_params["usernames"] = utils.commajoin(usernames)
            query_params["provision"] = (
                "false" if str(provision).lower() == "false" else "true"
            )
        if ids:
            query_params["ids"] = utils.commajoin(ids)

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
        :param ids: An identity provider ID or iterable of IDs to lookup. Mutually exclusive
            with ``domains``.
        :param query_params: Any additional parameters to be passed through
            as query params.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get by ID
                    >>> r = ac.get_identity_providers(ids="41143743-f3c8-4d60-bbdb-eeecaba85bd9")
                    >>> r.data
                    {
                      'identity_providers': [
                        {
                          'alternative_names': [],
                          'name': 'Globus ID',
                          'domains': ['globusid.org'],
                          'id': '41143743-f3c8-4d60-bbdb-eeecaba85bd9',
                          'short_name': 'globusid'
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
            query_params["domains"] = utils.commajoin(domains)
        elif ids is not None:
            query_params["ids"] = utils.commajoin(ids)
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

    def get_project(self, project_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Look up a project. Requires the ``manage_projects`` scope.

        :param project_id: The ID of the project to lookup

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_project("927d7238-f917-4eb2-9ace-c523fa9ba34e")
                    >>> r.data
                    {
                      'project': {
                        'admin_ids': ['41143743-f3c8-4d60-bbdb-eeecaba85bd9']
                        'contact_email': 'support@globus.org',
                        'display_name': 'Globus SDK Demo Project',
                        'admin_group_ids': None,
                        'id': '927d7238-f917-4eb2-9ace-c523fa9ba34e',
                        'project_name': 'Globus SDK Demo Project',
                        'admins': {
                          'identities': ['41143743-f3c8-4d60-bbdb-eeecaba85bd9'],
                          'groups': [],
                        },
                      }
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_project

            .. tab-item:: API Info

                ``GET /v2/api/projects/{project_id}``

                .. extdoclink:: Get Projects
                    :ref: auth/reference/#get_projects
        """
        return self.get(f"/v2/api/projects/{project_id}")

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
                      'projects': [
                        {
                          'admin_ids': ['41143743-f3c8-4d60-bbdb-eeecaba85bd9']
                          'contact_email': 'support@globus.org',
                          'display_name': 'Globus SDK Demo Project',
                          'admin_group_ids': None,
                          'id': '927d7238-f917-4eb2-9ace-c523fa9ba34e',
                          'project_name': 'Globus SDK Demo Project',
                          'admins': {
                            'identities': ['41143743-f3c8-4d60-bbdb-eeecaba85bd9'],
                            'groups': [],
                          },
                        }
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
        :param contact_email: The email address of the project's point of contact
        :param admin_ids: A list of user IDs to be added as admins of the project
        :param admin_group_ids: A list of group IDs to be added as admins of the project

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
        :param display_name: The name of the project
        :param contact_email: The email address of the project's point of contact
        :param admin_ids: A list of user IDs to be set as admins of the project
        :param admin_group_ids: A list of group IDs to be set as admins of the project

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

    def get_policy(self, policy_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Look up a policy. Requires the ``manage_projects`` scope.

        :param policy_id: The ID of the policy to lookup

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_policy("f5eaae7e-807f-41be-891a-ec86ff88df8f")
                    >>> r.data
                    {
                      'policy': {
                        'high_assurance': False,
                        'domain_constraints_include': ['globus.org'],
                        'display_name': 'Display Name',
                        'description': 'Description',
                        'id': 'f5eaae7e-807f-41be-891a-ec86ff88df8f',
                        'domain_constraints_exclude': None,
                        'project_id': 'da84e531-1afb-43cb-8c87-135ab580516a',
                        'authentication_assurance_timeout': 35
                      }
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_policy

            .. tab-item:: API Info

                ``GET /v2/api/policies/{policy_id}``

                .. extdoclink:: Get Policies
                    :ref: auth/reference/#get_policies
        """
        return self.get(f"/v2/api/policies/{policy_id}")

    def get_policies(self) -> IterableResponse:
        """
        Look up policies in projects on which the authenticated user is an admin.
        Requires the ``manage_projects`` scope.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_policies()
                    >>> r.data
                    {
                      'policies': [
                        {
                          'high_assurance': False,
                          'domain_constraints_include': ['greenlight.org'],
                          'display_name': 'GreenLight domain Only Policy',
                          'description': 'Only allow access from @greenlight.org',
                          'id': '99d2dc75-3acb-48ff-b5e5-2eee0a5121d1',
                          'domain_constraints_exclude': None,
                          'project_id': 'da84e531-1afb-43cb-8c87-135ab580516a',
                          'authentication_assurance_timeout': 35,
                        },
                        {
                          'high_assurance': True,
                          'domain_constraints_include': None,
                          'display_name': 'No RedLight domain Policy',
                          'description': 'Disallow access from @redlight.org',
                          'id': '5d93ebf0-b4c6-4928-9929-4ac47fc2786d',
                          'domain_constraints_exclude': ['redlight.org'],
                          'project_id': 'da84e531-1afb-43cb-8c87-135ab580516a',
                          'authentication_assurance_timeout': 35,
                        }
                      ]
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_policies

            .. tab-item:: API Info

                ``GET /v2/api/policies``

                .. extdoclink:: Get Policies
                    :ref: auth/reference/#get_policies
        """
        return GetPoliciesResponse(self.get("/v2/api/policies"))

    @_create_policy_compat
    def create_policy(  # pylint: disable=missing-param-doc
        self,
        *,
        project_id: UUIDLike,
        display_name: str,
        description: str,
        high_assurance: bool | utils.MissingType = utils.MISSING,
        authentication_assurance_timeout: int | utils.MissingType = utils.MISSING,
        domain_constraints_include: (
            t.Iterable[str] | None | utils.MissingType
        ) = utils.MISSING,
        domain_constraints_exclude: (
            t.Iterable[str] | None | utils.MissingType
        ) = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Create a new Auth policy. Requires the ``manage_projects`` scope.

        :param project_id: ID of the project for the new policy
        :param high_assurance: Whether or not this policy is applied to sessions.
        :param authentication_assurance_timeout: Number of seconds within which someone
            must have authenticated to satisfy the policy
        :param display_name: A user-friendly name for the policy
        :param description: A user-friendly description to explain the purpose of the
            policy
        :param domain_constraints_include: A list of domains that can satisfy the policy
        :param domain_constraints_exclude: A list of domains that cannot satisfy the
            policy

        .. note:

            ``project_id``, ``display_name``, and ``description`` are all required
            arguments, although they are not declared as required in the function
            signature. This is due to a backwards compatible behavior with earlier
            versions of globus-sdk, and will be changed in a future release which
            removes the compatible behavior.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> r = ac.create_policy(
                    ...     project_id="da84e531-1afb-43cb-8c87-135ab580516a",
                    ...     high_assurance=True,
                    ...     authentication_assurance_timeout=35,
                    ...     display_name="No RedLight domain Policy",
                    ...     description="Disallow access from @redlight.org",
                    ...     domain_constraints_exclude=["redlight.org"],
                    ... )
                    >>> policy_id = r["policy"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_policy

            .. tab-item:: API Info

                ``POST /v2/api/policies``

                .. extdoclink:: Create Policy
                    :ref: auth/reference/#create_policy
        """
        body: dict[str, t.Any] = {
            "project_id": project_id,
            "high_assurance": high_assurance,
            "authentication_assurance_timeout": authentication_assurance_timeout,
            "display_name": display_name,
            "description": description,
            "domain_constraints_include": domain_constraints_include,
            "domain_constraints_exclude": domain_constraints_exclude,
        }

        return self.post("/v2/api/policies", data={"policy": body})

    def update_policy(
        self,
        policy_id: UUIDLike,
        *,
        project_id: UUIDLike | utils.MissingType = utils.MISSING,
        authentication_assurance_timeout: int | utils.MissingType = utils.MISSING,
        display_name: str | utils.MissingType = utils.MISSING,
        description: str | utils.MissingType = utils.MISSING,
        domain_constraints_include: (
            t.Iterable[str] | None | utils.MissingType
        ) = utils.MISSING,
        domain_constraints_exclude: (
            t.Iterable[str] | None | utils.MissingType
        ) = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Update a policy. Requires the ``manage_projects`` scope.

        :param policy_id: ID of the policy to update
        :param project_id: ID of the project for the new policy
        :param authentication_assurance_timeout: Number of seconds within which someone
            must have authenticated to satisfy the policy
        :param display_name: A user-friendly name for the policy
        :param description: A user-friendly description to explain the purpose of the
            policy
        :param domain_constraints_include: A list of domains that can satisfy the policy
        :param domain_constraints_exclude: A list of domains that can not satisfy the
            policy

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> policy_id = ...
                    >>> r = ac.update_policy(scope_id, display_name="Greenlight Policy")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.update_policy

            .. tab-item:: API Info

                ``POST /v2/api/policies/{policy_id}``

                .. extdoclink:: Update Policy
                    :ref: auth/reference/#update_policy
        """
        body: dict[str, t.Any] = {
            "authentication_assurance_timeout": authentication_assurance_timeout,
            "display_name": display_name,
            "description": description,
            "domain_constraints_include": domain_constraints_include,
            "domain_constraints_exclude": domain_constraints_exclude,
            "project_id": project_id,
        }
        return self.put(f"/v2/api/policies/{policy_id}", data={"policy": body})

    def delete_policy(self, policy_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a policy. Requires the ``manage_projects`` scope.

        :param policy_id: The ID of the policy to delete

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> policy_id = ...
                    >>> r = ac.delete_policy(policy_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_policy

            .. tab-item:: API Info

                ``DELETE /v2/api/policies/{policy_id}``

                .. extdoclink:: Delete Policy
                    :ref: auth/reference/#delete_policy
        """
        return self.delete(f"/v2/api/policies/{policy_id}")

    def get_client(
        self,
        *,
        client_id: UUIDLike | utils.MissingType = utils.MISSING,
        fqdn: str | utils.MissingType = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Look up a client by ``client_id`` or (exclusive) by ``fqdn``.
        Requires the ``manage_projects`` scope.

        :param client_id: The ID of the client to look up
        :param fqdn: The fully-qualified domain name of the client to look up

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # by client_id
                    >>> r = ac.get_client(client_id="6336437e-37e8-4559-82a8-674390c1fd2e")
                    >>> r.data
                    {
                      'client': {
                        'required_idp': None,
                        'name': 'Great client of FOO',
                        'redirect_uris': [],
                        'links': {
                          'privacy_policy': None,
                          'terms_and_conditions': None
                        },
                        'scopes': [],
                        'grant_types': [
                          'authorization_code',
                          'client_credentials',
                          'refresh_token'
                        ],
                        'id': '6336437e-37e8-4559-82a8-674390c1fd2e',
                        'prompt_for_named_grant': False,
                        'fqdns': ['globus.org'],
                        'project': 'da84e531-1afb-43cb-8c87-135ab580516a',
                        'client_type': 'client_identity',
                        'visibility': 'private',
                        'parent_client': None,
                        'userinfo_from_effective_identity': True,
                        'preselect_idp': None,
                        'public_client': False
                      }
                    }
                    >>> # by fqdn
                    >>> fqdn = ...
                    >>> r = ac.get_client(fqdn=fqdn)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_client

            .. tab-item:: API Info

                ``GET /v2/api/clients/{client_id}``
                ``GET /v2/api/clients?fqdn={fqdn}``

                .. extdoclink:: Get Clients
                    :ref: auth/reference/#get_clients
        """  # noqa: E501
        if client_id is not utils.MISSING and fqdn is not utils.MISSING:
            raise exc.GlobusSDKUsageError(
                "AuthClient.get_client does not take both "
                "'client_id' and 'fqdn'. These are mutually exclusive."
            )

        if client_id is utils.MISSING and fqdn is utils.MISSING:
            raise exc.GlobusSDKUsageError(
                "AuthClient.get_client requires either 'client_id' or 'fqdn'."
            )

        if client_id is not utils.MISSING:
            return self.get(f"/v2/api/clients/{client_id}")
        return self.get("/v2/api/clients", query_params={"fqdn": fqdn})

    def get_clients(self) -> IterableResponse:
        """
        Look up clients in projects on which the authenticated user is an admin.
        Requires the ``manage_projects`` scope.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_clients()
                    >>> r.data
                    {
                      'clients': [
                        {
                          'required_idp': None,
                          'name': 'Great client of FOO',
                          'redirect_uris': [],
                          'links': {'privacy_policy': None, 'terms_and_conditions': None},
                          'scopes': [],
                          'grant_types': ['authorization_code', 'client_credentials', 'refresh_token'],
                          'id': 'b6001d11-8765-49d3-a503-ba323fc74eee',
                          'prompt_for_named_grant': False,
                          'fqdns': ['foo.net'],
                          'project': 'da84e531-1afb-43cb-8c87-135ab580516a',
                          'client_type': 'client_identity',
                          'visibility': 'private',
                          'parent_client': None,
                          'userinfo_from_effective_identity': True,
                          'preselect_idp': None,
                          'public_client': False,
                        },
                        {
                          'required_idp': None,
                          'name': 'Lessor client of BAR',
                          'redirect_uris': [],
                          'links': {'privacy_policy': None, 'terms_and_conditions': None},
                          'scopes': [],
                          'grant_types': ['authorization_code', 'client_credentials', 'refresh_token'],
                          'id': 'b87f7415-ddf9-4868-8e55-d10c065f733d',
                          'prompt_for_named_grant': False,
                          'fqdns': ['bar.org'],
                          'project': 'da84e531-1afb-43cb-8c87-135ab580516a',
                          'client_type': 'client_identity',
                          'visibility': 'private',
                          'parent_client': None,
                          'userinfo_from_effective_identity': True,
                          'preselect_idp': None,
                          'public_client': False,
                        }
                      ]
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_clients

            .. tab-item:: API Info

                ``GET /v2/api/clients``

                .. extdoclink:: Get Clients
                    :ref: auth/reference/#get_clients
        """  # noqa: E501
        return GetClientsResponse(self.get("/v2/api/clients"))

    def create_client(
        self,
        name: str,
        project: UUIDLike,
        *,
        public_client: bool | utils.MissingType = utils.MISSING,
        client_type: (
            utils.MissingType
            | t.Literal[
                "client_identity",
                "confidential_client",
                "globus_connect_server",
                "public_installed_client",
                "hybrid_confidential_client_resource_server",
                "resource_server",
            ]
        ) = utils.MISSING,
        visibility: utils.MissingType | t.Literal["public", "private"] = utils.MISSING,
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
        :param project: ID representing the project this client belongs to.

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
                    >>> project = ...
                    >>> r = ac.create_client(
                    ...     "My client",
                    ...     True,
                    ...     project,
                    ...     True,
                    ... )
                    >>> client_id = r["client"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_client

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
            "project": project,
            "visibility": visibility,
            "redirect_uris": redirect_uris,
            "required_idp": required_idp,
            "preselect_idp": preselect_idp,
            "public_client": public_client,
            "client_type": client_type,
        }
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

    def update_client(
        self,
        client_id: UUIDLike,
        *,
        name: str | utils.MissingType = utils.MISSING,
        visibility: utils.MissingType | t.Literal["public", "private"] = utils.MISSING,
        redirect_uris: t.Iterable[str] | utils.MissingType = utils.MISSING,
        terms_and_conditions: str | None | utils.MissingType = utils.MISSING,
        privacy_policy: str | None | utils.MissingType = utils.MISSING,
        required_idp: UUIDLike | None | utils.MissingType = utils.MISSING,
        preselect_idp: UUIDLike | None | utils.MissingType = utils.MISSING,
        additional_fields: dict[str, t.Any] | utils.MissingType = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Update a client. Requires the ``manage_projects`` scope.

        :param client_id: ID of the client to update
        :param name: The display name shown to users on consents. May not contain
            linebreaks.
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

                When creating a project, your account is not necessarily included as an
                admin. The following snippet uses the ``manage_projects`` scope as well
                as the ``openid`` and ``email`` scopes to get the current user ID and
                email address and use those data to setup the project.

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> r = ac.create_update(client_id, name="Foo Utility")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.update_client

            .. tab-item:: API Info

                ``POST /v2/api/clients/{client_id}``

                .. extdoclink:: Update Client
                    :ref: auth/reference/#update_client
        """
        body: dict[str, t.Any] = {
            "name": name,
            "visibility": visibility,
            "redirect_uris": redirect_uris,
            "required_idp": required_idp,
            "preselect_idp": preselect_idp,
        }

        # terms_and_conditions and privacy_policy must both be set or unset, and if one
        # is set to `None` they both must be set to `None`
        # note the subtle differences between this logic for "update" and the matching
        # logic for "create"
        # "create" does not need to handle `None` as a distinct and meaningful value
        if type(terms_and_conditions) is not type(privacy_policy):
            raise exc.GlobusSDKUsageError(
                "terms_and_conditions and privacy_policy must both be set or unset"
            )
        links: dict[str, str | None | utils.MissingType] = {
            "terms_and_conditions": terms_and_conditions,
            "privacy_policy": privacy_policy,
        }
        if (
            terms_and_conditions is not utils.MISSING
            or privacy_policy is not utils.MISSING
        ):
            body["links"] = links

        if not isinstance(additional_fields, utils.MissingType):
            body.update(additional_fields)

        return self.put(f"/v2/api/clients/{client_id}", data={"client": body})

    def delete_client(self, client_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a client. Requires the ``manage_projects`` scope.

        :param client_id: The ID of the client to delete

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> r = ac.delete_policy(client_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_client

            .. tab-item:: API Info

                ``DELETE /v2/api/clients/{client_id}``

                .. extdoclink:: Delete Client
                    :ref: auth/reference/#delete_client
        """
        return self.delete(f"/v2/api/clients/{client_id}")

    def get_client_credentials(self, client_id: UUIDLike) -> IterableResponse:
        """
        Look up client credentials by ``client_id``.  Requires the
        ``manage_projects`` scope.

        :param client_id: The ID of the client that owns the credentials

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_credentials("6336437e-37e8-4559-82a8-674390c1fd2e")
                    >>> r.data
                    {
                      'credentials': [
                        'name': 'foo',
                        'id': 'cf88318e-b2dd-43fd-8ea5-2086fc69ffac',
                        'created': '2023-10-21T22:46:15.845937+00:00',
                        'client': '6336437e-37e8-4559-82a8-674390c1fd2e',
                        'secret': None,
                      ]
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_client_credentials

            .. tab-item:: API Info

                ``GET /v2/api/clients/{client_id}/credentials``

                .. extdoclink:: Get Client Credentials
                    :ref: auth/reference/#get_client_credentials
        """  # noqa: E501
        return GetClientCredentialsResponse(
            self.get(f"/v2/api/clients/{client_id}/credentials")
        )

    def create_client_credential(
        self,
        client_id: UUIDLike,
        name: str,
    ) -> GlobusHTTPResponse:
        """
        Create a new client credential. Requires the ``manage_projects`` scope.

        :param client_id: ID for the client
        :param name: The display name of the new credential.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> name = ...
                    >>> r = ac.create_client_credential(
                    ...     "25afc56d-02af-4175-8c90-9941ebb623dd",
                    ...     "New Credentials",
                    ... )
                    >>> r.data
                    {
                        'name': 'New Credentials',
                        'id': '3a53cb4d-edd6-4ae3-900e-25b38b5fce02',
                        'created': '2023-10-21T22:46:15.845937+00:00',
                        'client': '25afc56d-02af-4175-8c90-9941ebb623dd',
                        'secret': 'abc123',
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_client_credential

            .. tab-item:: API Info

                ``POST /v2/api/clients/{client_id}/credentials``

                .. extdoclink:: Create Client Credentials
                    :ref: auth/reference/#create_client_credential
        """
        return self.post(
            f"/v2/api/clients/{client_id}/credentials",
            data={"credential": {"name": name}},
        )

    def delete_client_credential(
        self,
        client_id: UUIDLike,
        credential_id: UUIDLike,
    ) -> GlobusHTTPResponse:
        """
        Delete a credential. Requires the ``manage_projects`` scope.

        :param client_id: The ID of the client that owns the credential to delete
        :param credential_id: The ID of the credential to delete

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> credential_id = ...
                    >>> r = ac.delete_policy(client_id, credential_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_client_credential

            .. tab-item:: API Info

                ``DELETE /v2/api/clients/{client_id}/credentials/{credential_id}``

                .. extdoclink:: Delete Credential
                    :ref: auth/reference/#delete_client_credentials
        """
        return self.delete(f"/v2/api/clients/{client_id}/credentials/{credential_id}")

    def get_scope(self, scope_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Look up a scope by ``scope_id``.  Requires the ``manage_projects`` scope.

        :param scope_id: The ID of the scope to look up

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_scope(scope_id="6336437e-37e8-4559-82a8-674390c1fd2e")
                    >>> r.data
                    {
                      'scope': {
                        'scope_string': 'https://auth.globus.org/scopes/3f33d83f-ec0a-4190-887d-0622e7c4ee9a/manager',
                        'allows_refresh_token': False,
                        'id': '87cf7b34-e1e1-4805-a8d5-51ab59fe6000',
                        'advertised': False,
                        'required_domains': [],
                        'name': 'Client manage scope',
                        'description': 'Manage configuration of this client',
                        'client': '3f33d83f-ec0a-4190-887d-0622e7c4ee9a',
                        'dependent_scopes': [],
                      }
                    }

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_scope

            .. tab-item:: API Info

                ``GET /v2/api/scopes/{scope_id}``

                .. extdoclink:: Get Scopes
                    :ref: auth/reference/#get_scopes
        """  # noqa: E501
        return self.get(f"/v2/api/scopes/{scope_id}")

    def get_scopes(
        self,
        *,
        scope_strings: t.Iterable[str] | str | utils.MissingType = utils.MISSING,
        ids: t.Iterable[UUIDLike] | UUIDLike | utils.MissingType = utils.MISSING,
        query_params: dict[str, t.Any] | utils.MissingType = utils.MISSING,
    ) -> IterableResponse:
        """
        Look up scopes in projects on which the authenticated user is an admin.
        The scopes response can be filted by ``scope_strings`` or (exclusive)
        ``ids``.  Requires the ``manage_projects`` scope.

        :param scope_strings: The scope_strings of the scopes to look up
        :param ids: The ID of the scopes to look up
        :param query_params: Any additional parameters to be passed through
            as query params.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get all scopes
                    >>> r = ac.get_scopes()
                    >>> r.data
                    {
                      'scopes': [
                        {
                          'scope_string': 'https://auth.globus.org/scopes/3f33d83f-ec0a-4190-887d-0622e7c4ee9a/manage',
                          'allows_refresh_token': False,
                          'id': '70147193-f88a-4da9-9d6e-677c15e790e5',
                          'advertised': False,
                          'required_domains': [],
                          'name': 'Client manage scope',
                          'description': 'Manage configuration of this client',
                          'client': '3f33d83f-ec0a-4190-887d-0622e7c4ee9a',
                          'dependent_scopes': [],
                        },
                        {
                          'scope_string': 'https://auth.globus.org/scopes/dfc9a6d3-3373-4a6d-b0a1-b7026d1559d6/view',
                          'allows_refresh_token': False,
                          'id': '3793042a-203c-4e86-8dfe-17d407d0bb5f',
                          'advertised': False,
                          'required_domains': [],
                          'name': 'Client view scope',
                          'description': 'View configuration of this client',
                          'client': 'dfc9a6d3-3373-4a6d-b0a1-b7026d1559d6',
                          'dependent_scopes': [],
                        }
                      ]
                    }

                    >>> # by all scope ids
                    >>> scope_ids = ...
                    >>> r = ac.get_scopes(ids=scopes_ides)

                    >>> # by all scope strings
                    >>> scope_strings = ...
                    >>> r = ac.get_scopes(scope_strings=scope_strings)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_scopes

            .. tab-item:: API Info

                ``GET /v2/api/scopes``
                ``GET /v2/api/scopes?ids=...``
                ``GET /v2/api/scopes?scope_strings=...``

                .. extdoclink:: Get Scopes
                    :ref: auth/reference/#get_scopes
        """  # noqa: E501
        if scope_strings is not utils.MISSING and ids is not utils.MISSING:
            raise exc.GlobusSDKUsageError(
                "AuthClient.get_scopes does not take both "
                "'scopes_strings' and 'ids'. These are mutually exclusive."
            )

        if isinstance(query_params, utils.MissingType):
            query_params = {}

        if not isinstance(scope_strings, utils.MissingType):
            query_params["scope_strings"] = utils.commajoin(scope_strings)
        if not isinstance(ids, utils.MissingType):
            query_params["ids"] = utils.commajoin(ids)

        return GetScopesResponse(self.get("/v2/api/scopes", query_params=query_params))

    def create_scope(
        self,
        client_id: UUIDLike,
        name: str,
        description: str,
        scope_suffix: str,
        *,
        required_domains: t.Iterable[str] | utils.MissingType = utils.MISSING,
        dependent_scopes: (
            t.Iterable[DependentScopeSpec] | utils.MissingType
        ) = utils.MISSING,
        advertised: bool | utils.MissingType = utils.MISSING,
        allows_refresh_token: bool | utils.MissingType = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Create a new scope. Requires the ``manage_projects`` scope.

        :param client_id: ID of the client for the new scope
        :param name: A display name used to display consents to users,
            along with description
        :param description: A description used to display consents to users, along with
            name
        :param scope_suffix: String consisting of lowercase letters, number, and
            underscores. This will be the final part of the scope_string
        :param required_domains: Domains the user must have linked identities in in
            order to make use of the scope
        :param dependent_scopes: Scopes included in the consent for this new scope
        :param advertised: If True, scope is visible to anyone regardless of client
            visibility, otherwise, scope visibility is based on client visibility.
        :param allows_refresh_token: Whether or not the scope allows refresh tokens
            to be issued.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> client_id = ...
                    >>> r = ac.create_scope(
                    ...     client_id,
                    ...     "Client Management",
                    ...     "Manage client configuration",
                    ...     "manage",
                    ... )
                    >>> scope_id = r["scope"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_scope

            .. tab-item:: API Info

                ``POST /v2/api/clients/{client_id}/scopes``

                .. extdoclink:: Create Scope
                    :ref: auth/reference/#create_scope
        """
        body: dict[str, t.Any] = {
            "name": name,
            "description": description,
            "scope_suffix": scope_suffix,
            "advertised": advertised,
            "allows_refresh_token": allows_refresh_token,
            "required_domains": required_domains,
            "dependent_scopes": dependent_scopes,
        }

        return self.post(f"/v2/api/clients/{client_id}/scopes", data={"scope": body})

    def update_scope(
        self,
        scope_id: UUIDLike,
        *,
        name: str | utils.MissingType = utils.MISSING,
        description: str | utils.MissingType = utils.MISSING,
        scope_suffix: str | utils.MissingType = utils.MISSING,
        required_domains: t.Iterable[str] | utils.MissingType = utils.MISSING,
        dependent_scopes: (
            t.Iterable[DependentScopeSpec] | utils.MissingType
        ) = utils.MISSING,
        advertised: bool | utils.MissingType = utils.MISSING,
        allows_refresh_token: bool | utils.MissingType = utils.MISSING,
    ) -> GlobusHTTPResponse:
        """
        Update a scope. Requires the ``manage_projects`` scope.

        :param scope_id: ID of the scope to update
        :param name: A display name used to display consents to users,
            along with description
        :param description: A description used to display consents to users, along with
            name
        :param scope_suffix: String consisting of lowercase letters, number, and
            underscores. This will be the final part of the scope_string
        :param required_domains: Domains the user must have linked identities in in
            order to make use of the scope
        :param dependent_scopes: Scopes included in the consent for this new scope
        :param advertised: If True, scope is visible to anyone regardless of client
            visibility, otherwise, scope visibility is based on client visibility.
        :param allows_refresh_token: Whether or not the scope allows refresh tokens
            to be issued.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> scope_id = ...
                    >>> r = ac.update_scope(scope_id, scope_suffix="manage")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.update_scope

            .. tab-item:: API Info

                ``POST /v2/api/scopes/{scope_id}``

                .. extdoclink:: Update Scope
                    :ref: auth/reference/#update_scope
        """
        body: dict[str, t.Any] = {
            "name": name,
            "description": description,
            "scope_suffix": scope_suffix,
            "advertised": advertised,
            "allows_refresh_token": allows_refresh_token,
            "required_domains": required_domains,
            "dependent_scopes": dependent_scopes,
        }

        return self.put(f"/v2/api/scopes/{scope_id}", data={"scope": body})

    def delete_scope(self, scope_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a scope. Requires the ``manage_projects`` scope.

        :param scope_id: The ID of the scope to delete

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> scope_id = ...
                    >>> r = ac.delete_scope(scope_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_scope

            .. tab-item:: API Info

                ``DELETE /v2/api/scopes/{scope_id}``

                .. extdoclink:: Delete Scopes
                    :ref: auth/reference/#delete_scope
        """
        return self.delete(f"/v2/api/scopes/{scope_id}")

    def get_consents(
        self,
        identity_id: UUIDLike,
        *,
        # pylint: disable=redefined-builtin
        all: bool = False,
    ) -> GetConsentsResponse:
        """
        Look up consents for a user.

        If requesting "all" consents, the view_consents scope is required.

        :param identity_id: The ID of the identity to look up consents for
        :param all: If true, return all consents, including those that have
            been issued to other clients. If false, return only consents rooted at this
            client id for the requested identity. Most clients should pass False.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> identity_id = ...
                    >>> forest = ac.get_consents(identity_id).to_forest()

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_consents

            .. tab-item:: API Info

                ``GET /v2/api/identities/{identity_id}/consents``
        """
        return GetConsentsResponse(
            self.get(
                f"/v2/api/identities/{identity_id}/consents", query_params={"all": all}
            )
        )
