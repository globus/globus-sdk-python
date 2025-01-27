from __future__ import annotations

import typing as t
import uuid

from globus_sdk import client, exc, paging, response, scopes, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.globus_app import GlobusApp
from globus_sdk.scopes import Scope

from .connector_table import ConnectorTable
from .data import (
    CollectionDocument,
    EndpointDocument,
    GCSRoleDocument,
    StorageGatewayDocument,
    UserCredentialDocument,
)
from .errors import GCSAPIError
from .response import IterableGCSResponse, UnpackingGCSResponse

C = t.TypeVar("C", bound=t.Callable[..., t.Any])


class GCSClient(client.BaseClient):
    """
    A GCSClient provides communication with the GCS Manager API of a Globus Connect
    Server instance.
    For full reference, see the `documentation for the GCS Manager API
    <https://docs.globus.org/globus-connect-server/v5/api/>`_.

    Unlike other client types, this must be provided with an address for the GCS
    Manager. All other arguments are the same as those for
    :class:`~globus_sdk.BaseClient`.

    .. sdk-sphinx-copy-params:: BaseClient

        :param gcs_address: The FQDN (DNS name) or HTTPS URL for the GCS Manager API.

    .. automethodlist:: globus_sdk.GCSClient
    """

    # TODO: under SDK v4.0, service_name should not be set
    service_name = "globus_connect_server"
    error_class = GCSAPIError

    def __init__(
        self,
        gcs_address: str,
        *,
        app: GlobusApp | None = None,
        app_scopes: list[Scope] | None = None,
        environment: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        # check if the provided address was a DNS name or an HTTPS URL
        if not gcs_address.startswith("https://"):
            # if it's a DNS name format it accordingly
            gcs_address = f"https://{gcs_address}/api/"
        # if it was an HTTPS URL, check that it ends with /api/
        elif not gcs_address.endswith(("/api/", "/api")):
            # if it doesn't, add it
            gcs_address = utils.slash_join(gcs_address, "/api/")

        self._endpoint_client_id: str | None = None

        super().__init__(
            base_url=gcs_address,
            environment=environment,
            app=app,
            app_scopes=app_scopes,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )

    @staticmethod
    def get_gcs_endpoint_scopes(
        endpoint_id: uuid.UUID | str,
    ) -> scopes.GCSEndpointScopeBuilder:
        """Given a GCS Endpoint ID, this helper constructs an object containing the
        scopes for that Endpoint.

        :param endpoint_id: The ID of the Endpoint

        See documentation for :class:`globus_sdk.scopes.GCSEndpointScopeBuilder` for
        more information.
        """
        return scopes.GCSEndpointScopeBuilder(str(endpoint_id))

    @staticmethod
    def get_gcs_collection_scopes(
        collection_id: uuid.UUID | str,
    ) -> scopes.GCSCollectionScopeBuilder:
        """Given a GCS Collection ID, this helper constructs an object containing the
        scopes for that Collection.

        :param collection_id: The ID of the Collection

        See documentation for :class:`globus_sdk.scopes.GCSCollectionScopeBuilder` for
        more information.
        """
        return scopes.GCSCollectionScopeBuilder(str(collection_id))

    @staticmethod
    def connector_id_to_name(connector_id: UUIDLike) -> str | None:
        """
        .. warning::

            This method is deprecated -- use
            ``ConnectorTable.lookup`` instead.

        Helper that converts a given connector ID into a human-readable
        connector name string.

        :param connector_id: The ID of the connector
        """
        exc.warn_deprecated(
            "`connector_id_to_name` has been replaced with "
            "`ConnectorTable.lookup`. Use that instead, "
            "and retrieve the `name` attribute from the result."
        )
        connector_obj = ConnectorTable.lookup(connector_id)
        if connector_obj is None:
            return None
        name = connector_obj.name
        # compatibility shim due to name change in the data (which was updated to
        # match internal sources referring to this only as "BlackPearl")
        if name == "BlackPearl":
            name = "Spectralogic BlackPearl"
        return name

    @property
    def default_scope_requirements(self) -> list[Scope]:
        return [
            Scope(
                GCSClient.get_gcs_endpoint_scopes(
                    self.endpoint_client_id
                ).manage_collections
            )
        ]

    @utils.classproperty
    def resource_server(  # pylint: disable=missing-param-doc
        self_or_cls: client.BaseClient | type[client.BaseClient],
    ) -> str | None:
        """
        The resource server for a GCS endpoint is the ID of its GCS Manager Client.

        This will return None if called as a classmethod as an instantiated
        ``GCSClient`` is required to look up the client ID from the endpoint.
        """
        if not isinstance(self_or_cls, GCSClient):
            return None

        return self_or_cls.endpoint_client_id

    @property
    def endpoint_client_id(self) -> str:
        """
        The UUID of the GCS Manager client of the endpoint this client is configured
        for. This will be equal to the ``endpoint_id`` in most cases, but when they
        differ the ``client_id`` is the canonical value for the endpoint's resource
        server and scopes.
        """
        if self._endpoint_client_id:
            return self._endpoint_client_id

        else:
            data = self.get_gcs_info()
            try:
                endpoint_id = str(data["client_id"])
            except KeyError:
                print(data)
            self._endpoint_client_id = endpoint_id
            return endpoint_id

    #
    # endpoint methods
    #

    def get_gcs_info(
        self, query_params: dict[str, t.Any] | None = None
    ) -> UnpackingGCSResponse:
        """
        Get information about the GCS Manager service this client is configured for.
        This call is made unauthenticated.

        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /info``

                .. extdoclink:: Get Endpoint
                    :ref: openapi/#getInfo
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.get("/info", query_params=query_params, automatic_authorization=False),
            "info",
        )

    def get_endpoint(
        self, query_params: dict[str, t.Any] | None = None
    ) -> UnpackingGCSResponse:
        """
        Get the details of the Endpoint that this client is configured to talk to.

        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint``

                .. extdoclink:: Get Endpoint
                    :ref: openapi_Endpoint/#getEndpoint
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.get("/endpoint", query_params=query_params),
            "endpoint",
        )

    def update_endpoint(
        self,
        endpoint_data: dict[str, t.Any] | EndpointDocument,
        *,
        include: (
            t.Iterable[t.Literal["endpoint"]] | t.Literal["endpoint"] | None
        ) = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Update a GCSv5 Endpoint

        :param endpoint_data: The endpoint document for the modified endpoint
        :param include: Optional list of document types to include in the response
           (currently only supports the value ``["endpoint"]``)
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PATCH /endpoint``

                .. extdoclink:: Update Endpoint
                    :ref: openapi_Endpoint/#patchEndpoint
                    :service: gcs
        """
        query_params = query_params or {}
        if include is not None:
            query_params["include"] = utils.commajoin(include)

        return UnpackingGCSResponse(
            self.patch(
                "/endpoint",
                data=endpoint_data,
                query_params=query_params,
            ),
            "endpoint",
        )

    #
    # collection methods
    #

    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_collection_list(
        self,
        *,
        mapped_collection_id: UUIDLike | None = None,
        filter: (  # pylint: disable=redefined-builtin
            str | t.Iterable[str] | None
        ) = None,
        include: str | t.Iterable[str] | None = None,
        page_size: int | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableGCSResponse:
        """
        List the Collections on an Endpoint

        :param mapped_collection_id: Filter collections which were created using this
            mapped collection ID.
        :param filter: Filter the returned set to any combination of the following:
            ``mapped_collections``, ``guest_collections``, ``managed_by_me``,
            ``created_by_me``.
        :param include: Names of additional documents to include in the response
        :param page_size: Number of results to return per page
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /collections``

                .. extdoclink:: List Collections
                    :ref: openapi_Collections/#ListCollections
                    :service: gcs
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        if page_size is not None:
            query_params["page_size"] = page_size
        if marker is not None:
            query_params["marker"] = marker
        if mapped_collection_id is not None:
            query_params["mapped_collection_id"] = mapped_collection_id
        if filter is not None:
            if isinstance(filter, str):
                filter = [filter]
            query_params["filter"] = ",".join(filter)
        return IterableGCSResponse(self.get("collections", query_params=query_params))

    def get_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Lookup a Collection on an Endpoint

        :param collection_id: The ID of the collection to lookup
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /collections/{collection_id}``

                .. extdoclink:: Get Collection
                    :ref: openapi_Collections/#getCollection
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.get(f"/collections/{collection_id}", query_params=query_params),
            "collection",
        )

    def create_collection(
        self,
        collection_data: dict[str, t.Any] | CollectionDocument,
    ) -> UnpackingGCSResponse:
        """
        Create a collection. This is used to create either a mapped or a guest
        collection. When created, a ``collection:administrator`` role for that
        collection will be created using the caller’s identity.

        In order to create a guest collection, the caller must have an identity that
        matches the Storage Gateway policies.

        In order to create a mapped collection, the caller must have an
        ``endpoint:administrator`` or ``endpoint:owner`` role.

        :param collection_data: The collection document for the new collection

        .. tab-set::

            .. tab-item:: API Info

                ``POST /collections``

                .. extdoclink:: Create Collection
                    :ref: openapi_Collections/#createCollection
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.post("/collections", data=collection_data), "collection"
        )

    def update_collection(
        self,
        collection_id: UUIDLike,
        collection_data: dict[str, t.Any] | CollectionDocument,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Update a Collection

        :param collection_id: The ID of the collection to update
        :param collection_data: The collection document for the modified collection
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PATCH /collections/{collection_id}``

                .. extdoclink:: Update Collection
                    :ref: openapi_Collections/#patchCollection
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.patch(
                f"/collections/{collection_id}",
                data=collection_data,
                query_params=query_params,
            ),
            "collection",
        )

    def delete_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a Collection

        :param collection_id: The ID of the collection to delete
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /collections/{collection_id}``

                .. extdoclink:: Delete Collection
                    :ref: openapi_Collections/#deleteCollection
                    :service: gcs
        """
        return self.delete(f"/collections/{collection_id}", query_params=query_params)

    #
    # storage gateway methods
    #

    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_storage_gateway_list(
        self,
        *,
        include: None | str | t.Iterable[str] = None,
        page_size: int | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableGCSResponse:
        """
        List Storage Gateways

        :param include: Optional document types to include in the response. If
            'private_policies' is included, then include private storage gateway
            policies in the attached storage_gateways document. This requires an
            ``administrator`` role on the Endpoint.
        :param page_size: Number of results to return per page
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: get_storage_gateway_list

            .. tab-item:: API Info

                ``GET /storage_gateways``

                .. extdoclink:: Delete Collection
                    :ref: openapi_Storage_Gateways/#getStorageGateways
                    :service: gcs
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        if page_size is not None:
            query_params["page_size"] = page_size
        if marker is not None:
            query_params["marker"] = marker
        return IterableGCSResponse(
            self.get("/storage_gateways", query_params=query_params)
        )

    def create_storage_gateway(
        self,
        data: dict[str, t.Any] | StorageGatewayDocument,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Create a Storage Gateway

        :param data: Data in the format of a Storage Gateway document, it is recommended
            to use the ``StorageGatewayDocument`` class to construct this data.
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``POST /storage_gateways``

                .. extdoclink:: Create Storage Gateway
                    :ref: openapi_Storage_Gateways/#postStorageGateway
                    :service: gcs
        """
        return UnpackingGCSResponse(
            self.post("/storage_gateways", data=data, query_params=query_params),
            "storage_gateway",
        )

    def get_storage_gateway(
        self,
        storage_gateway_id: UUIDLike,
        *,
        include: None | str | t.Iterable[str] = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Lookup a Storage Gateway by ID

        :param storage_gateway_id: UUID for the Storage Gateway to be gotten
        :param include: Optional document types to include in the response. If
            'private_policies' is included, then include private storage gateway
            policies in the attached storage_gateways document. This requires an
            ``administrator`` role on the Endpoint.
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /storage_gateways/<storage_gateway_id>``

                .. extdoclink:: Get a Storage Gateway
                    :ref: openapi_Storage_Gateways/#getStorageGateway
                    :service: gcs
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))

        return UnpackingGCSResponse(
            self.get(
                f"/storage_gateways/{storage_gateway_id}",
                query_params=query_params,
            ),
            "storage_gateway",
        )

    def update_storage_gateway(
        self,
        storage_gateway_id: UUIDLike,
        data: dict[str, t.Any] | StorageGatewayDocument,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Update a Storage Gateway

        :param storage_gateway_id: UUID for the Storage Gateway to be updated
        :param data: Data in the format of a Storage Gateway document, it is recommended
            to use the ``StorageGatewayDocument`` class to construct this data.
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PATCH /storage_gateways/<storage_gateway_id>``

                .. extdoclink:: Update a Storage Gateway
                    :ref: openapi_Storage_Gateways/#patchStorageGateway
                    :service: gcs
        """
        return self.patch(
            f"/storage_gateways/{storage_gateway_id}",
            data=data,
            query_params=query_params,
        )

    def delete_storage_gateway(
        self,
        storage_gateway_id: str | uuid.UUID,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a Storage Gateway

        :param storage_gateway_id: UUID for the Storage Gateway to be deleted
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /storage_gateways/<storage_gateway_id>``

                .. extdoclink:: Delete a Storage Gateway
                    :ref: openapi_Storage_Gateways/#deleteStorageGateway
                    :service: gcs
        """
        return self.delete(
            f"/storage_gateways/{storage_gateway_id}", query_params=query_params
        )

    #
    # role methods
    #

    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_role_list(
        self,
        collection_id: UUIDLike | None = None,
        include: str | None = None,
        page_size: int | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableGCSResponse:
        """
        List Roles

        :param collection_id: UUID of a Collection. If given then only roles
            related to that Collection are returned, otherwise only Endpoint
            roles are returned.
        :param include: Pass "all_roles" to request all roles
            relevant to the resource instead of only those the caller has on
            the resource
        :param page_size: Number of results to return per page
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /roles``

                .. extdoclink:: Delete a Storage Gateway
                    :ref: openapi_Roles/#listRoles
                    :service: gcs
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = include
        if page_size is not None:
            query_params["page_size"] = page_size
        if marker is not None:
            query_params["marker"] = marker
        if collection_id is not None:
            query_params["collection_id"] = collection_id

        path = "/roles"
        return IterableGCSResponse(self.get(path, query_params=query_params))

    def create_role(
        self,
        data: dict[str, t.Any] | GCSRoleDocument,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Create a Role

        :param data: Data in the format of a Role document, it is recommended
            to use the `GCSRoleDocument` class to construct this data.
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``POST /roles``

                .. extdoclink:: Create Role
                    :ref: openapi_Roles/#postRole
                    :service: gcs
        """
        path = "/roles"
        return UnpackingGCSResponse(
            self.post(path, data=data, query_params=query_params),
            "role",
        )

    def get_role(
        self,
        role_id: UUIDLike,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Get a Role by ID

        :param role_id: UUID for the Role to be gotten
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /roles/{role_id}``

                .. extdoclink:: Get Role
                    :ref: openapi_Roles/#getRole
                    :service: gcs
        """
        path = f"/roles/{role_id}"
        return UnpackingGCSResponse(self.get(path, query_params=query_params), "role")

    def delete_role(
        self,
        role_id: UUIDLike,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a Role

        :param role_id: UUID for the Role to be deleted
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /roles/{role_id}``

                .. extdoclink:: Delete Role
                    :ref: openapi_Roles/#deleteRole
                    :service: gcs
        """
        path = f"/roles/{role_id}"
        return self.delete(path, query_params=query_params)

    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_user_credential_list(
        self,
        storage_gateway: UUIDLike | None = None,
        query_params: dict[str, t.Any] | None = None,
        page_size: int | None = None,
        marker: str | None = None,
    ) -> IterableGCSResponse:
        """
        List User Credentials

        :param storage_gateway: UUID of a storage gateway to limit results to
        :param query_params: Additional passthrough query parameters
        :param page_size: Number of results to return per page
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size

        .. tab-set::

            .. tab-item:: API Info

                ``GET /user_credentials``

                .. extdoclink:: Get User Credential List
                    :ref: openapi_User_Credentials/#getUserCredentials
                    :service: gcs
        """
        if query_params is None:
            query_params = {}
        if storage_gateway is not None:
            query_params["storage_gateway"] = storage_gateway
        if page_size is not None:
            query_params["page_size"] = page_size
        if marker is not None:
            query_params["marker"] = marker

        path = "/user_credentials"
        return IterableGCSResponse(self.get(path, query_params=query_params))

    def create_user_credential(
        self,
        data: dict[str, t.Any] | UserCredentialDocument,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Create a User Credential

        :param data: Data in the format of a UserCredential document, it is
            recommended to use the `UserCredential` class to construct this
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``POST /user_credentials``

                .. extdoclink:: Create User Credential
                    :ref: openapi_User_Credentials/#postUserCredential
                    :service: gcs
        """
        path = "/user_credentials"
        return UnpackingGCSResponse(
            self.post(path, data=data, query_params=query_params),
            "user_credential",
        )

    def get_user_credential(
        self,
        user_credential_id: UUIDLike,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Get a User Credential by ID

        :param user_credential_id: UUID for the UserCredential to be gotten
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /user_credentials/{user_credential_id}``

                .. extdoclink:: Get a User Credential
                    :ref: openapi_User_Credentials/#getUserCredential
                    :service: gcs
        """
        path = f"/user_credentials/{user_credential_id}"
        return UnpackingGCSResponse(
            self.get(path, query_params=query_params), "user_credential"
        )

    def update_user_credential(
        self,
        user_credential_id: UUIDLike,
        data: dict[str, t.Any] | UserCredentialDocument,
        query_params: dict[str, t.Any] | None = None,
    ) -> UnpackingGCSResponse:
        """
        Update a User Credential

        :param user_credential_id: UUID for the UserCredential to be updated
        :param data: Data in the format of a UserCredential document, it is
            recommended to use the `UserCredential` class to construct this
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PATCH /user_credentials/{user_credential_id}``

                .. extdoclink:: Update a User Credential
                    :ref: openapi_User_Credentials/#patchUserCredential
                    :service: gcs
        """
        path = f"/user_credentials/{user_credential_id}"
        return UnpackingGCSResponse(
            self.patch(path, data=data, query_params=query_params), "user_credential"
        )

    def delete_user_credential(
        self,
        user_credential_id: UUIDLike,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a User Credential

        :param user_credential_id: UUID for the UserCredential to be deleted
        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /user_credentials/{user_credential_id}``

                .. extdoclink:: Delete User Credential
                    :ref: openapi_User_Credentials/#deleteUserCredential
                    :service: gcs
        """
        path = f"/user_credentials/{user_credential_id}"
        return self.delete(path, query_params=query_params)
