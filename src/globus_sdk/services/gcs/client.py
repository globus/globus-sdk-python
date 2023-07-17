from __future__ import annotations

import typing as t
import uuid

from globus_sdk import client, paging, response, scopes, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer

from .data import (
    CollectionDocument,
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

    :param gcs_address: The FQDN (DNS name) or HTTPS URL for the GCS Manager API.
    :type gcs_address: str

    .. automethodlist:: globus_sdk.GCSClient
    """

    # TODO: under SDK v4.0, service_name should not be set
    service_name = "globus_connect_server"
    error_class = GCSAPIError

    def __init__(
        self,
        gcs_address: str,
        *,
        environment: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ):
        # check if the provided address was a DNS name or an HTTPS URL
        # if it was a URL, do not modify, but if it's a DNS name format it accordingly
        # as a heuristic for this: just check if string starts with "https://" (this is
        # sufficient to distinguish between the two for valid inputs)
        if not gcs_address.startswith("https://"):
            gcs_address = f"https://{gcs_address}/api/"
        super().__init__(
            base_url=gcs_address,
            environment=environment,
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
        :type endpoint_id: UUID or str

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
        :type collection_id: UUID or str

        See documentation for :class:`globus_sdk.scopes.GCSCollectionScopeBuilder` for
        more information.
        """
        return scopes.GCSCollectionScopeBuilder(str(collection_id))

    @staticmethod
    def connector_id_to_name(connector_id: UUIDLike) -> str | None:
        """
        Helper that converts a given connector_id into a human readable
        connector name string. Will return None if the id is not recognized.

        Note that it is possible for valid connector_ids to be unrecognized
        due to differing SDK and GCS versions.
        """
        connector_dict = {
            "7c100eae-40fe-11e9-95a3-9cb6d0d9fd63": "Box",
            "1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72": "Ceph",
            "56366b96-ac98-11e9-abac-9cb6d0d9fd63": "Google Cloud Storage",
            "976cf0cf-78c3-4aab-82d2-7c16adbcc281": "Google Drive",
            "145812c8-decc-41f1-83cf-bb2a85a2a70b": "POSIX",
            "7643e831-5f6c-4b47-a07f-8ee90f401d23": "S3",
            "7e3f3f5e-350c-4717-891a-2f451c24b0d4": "SpectraLogic BlackPearl",
        }
        return connector_dict.get(str(connector_id))

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
        :type mapped_collection_id: str or UUID
        :param filter: Filter the returned set to any combination of the following:
            ``mapped_collections``, ``guest_collections``, ``managed_by_me``,
            ``created_by_me``.
        :type filter: str or iterable of str, optional
        :param include: Names of additional documents to include in the response
        :type include: str or iterable of str, optional
        :param page_size: Number of results to return per page
        :type page_size: int, optional
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :type marker: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type collection_data: dict or CollectionDocument

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
        :type collection_id: str or UUID
        :param collection_data: The collection document for the modified collection
        :type collection_data: dict or CollectionDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type include: str or iterable of str, optional
        :param page_size: Number of results to return per page
        :type page_size: int, optional
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :type marker: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type data: dict or StorageGatewayDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type storage_gateway_id: str or UUID
        :param include: Optional document types to include in the response. If
            'private_policies' is included, then include private storage gateway
            policies in the attached storage_gateways document. This requires an
            ``administrator`` role on the Endpoint.
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type storage_gateway_id: str or UUID
        :param data: Data in the format of a Storage Gateway document, it is recommended
            to use the ``StorageGatewayDocument`` class to construct this data.
        :type data: dict or StorageGatewayDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type storage_gateway_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type collection_id: str or UUID, optional
        :param include: Pass "all_roles" to request all roles all roles
            relevant to the resource instead of only those the caller has on
            the resource
        :param page_size: Number of results to return per page
        :type page_size: int, optional
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :type marker: str, optional
        :type include: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type role_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type role_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type storage_gateway: str or UUID, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        :param page_size: Number of results to return per page
        :type page_size: int, optional
        :param marker: Pagination marker supplied by previous API calls in the event
            a request returns more values than the page size
        :type marker: str, optional

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
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type user_credential_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type user_credential_id: str or UUID
        :param data: Data in the format of a UserCredential document, it is
            recommended to use the `UserCredential` class to construct this
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

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
        :type user_credential_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /user_credentials/{user_credential_id}``

                .. extdoclink:: Delete User Credential
                    :ref: openapi_User_Credentials/#deleteUserCredential
                    :service: gcs
        """
        path = f"/user_credentials/{user_credential_id}"
        return self.delete(path, query_params=query_params)
