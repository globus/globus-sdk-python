import uuid
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar, Union

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

C = TypeVar("C", bound=Callable[..., Any])


def _gcsdoc(message: str, link: str) -> Callable[[C], C]:
    # do not use functools.partial because it doesn't preserve type information
    # see: https://github.com/python/mypy/issues/1484
    def partial(func: C) -> C:
        return utils.doc_api_method(
            message,
            link,
            external_base_url="https://docs.globus.org/globus-connect-server/v5/api",
        )(func)

    return partial


class GCSClient(client.BaseClient):
    """
    A GCSClient provides communication with the GCS Manager API of a Globus Connect
    Server instance.
    For full reference, see the `documentation for the GCS Manager API
    <https://docs.globus.org/globus-connect-server/v5/api/>`_.

    Unlike other client types, this must be provided with an address for the GCS
    Manager. All other arguments are the same as those for `~globus_sdk.BaseClient`.

    :param gcs_address: The FQDN (DNS name) or HTTPS URL for the GCS Manager API.
    :type gcs_address: str

    .. automethodlist:: globus_sdk.GCSClient
    """

    service_name = "globus_connect_server"
    error_class = GCSAPIError

    def __init__(
        self,
        gcs_address: str,
        *,
        environment: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
        app_name: Optional[str] = None,
        transport_params: Optional[Dict[str, Any]] = None,
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
        endpoint_id: Union[uuid.UUID, str]
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
        collection_id: Union[uuid.UUID, str]
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
    def connector_id_to_name(connector_id: UUIDLike) -> Optional[str]:
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

    @_gcsdoc("List Collections", "openapi_Collections/#ListCollections")
    def get_collection_list(
        self,
        *,
        mapped_collection_id: Optional[UUIDLike] = None,
        filter: Union[  # pylint: disable=redefined-builtin
            str, Iterable[str], None
        ] = None,
        include: Union[str, Iterable[str], None] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        ``GET /collections``

        :param mapped_collection_id: Filter collections which were created using this
            mapped collection ID.
        :type mapped_collection_id: str or UUID
        :param filter: Filter the returned set to any combination of the following:
            ``mapped_collections``, ``guest_collections``, ``managed_by_me``,
            ``created_by_me``.
        :type filter: str or iterable of str, optional
        :param include: Names of additional documents to include in the response
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        List the Collections on an Endpoint
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        if mapped_collection_id is not None:
            query_params["mapped_collection_id"] = mapped_collection_id
        if filter is not None:
            if isinstance(filter, str):
                filter = [filter]
            query_params["filter"] = ",".join(filter)
        return IterableGCSResponse(self.get("collections", query_params=query_params))

    @_gcsdoc("Get Collection", "openapi_Collections/#getCollection")
    def get_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        ``GET /collections/{collection_id}``

        :param collection_id: The ID of the collection to lookup
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        Lookup a Collection on an Endpoint
        """
        return UnpackingGCSResponse(
            self.get(f"/collections/{collection_id}", query_params=query_params),
            "collection",
        )

    @_gcsdoc("Create Collection", "openapi_Collections/#createCollection")
    def create_collection(
        self,
        collection_data: Union[Dict[str, Any], CollectionDocument],
    ) -> UnpackingGCSResponse:
        """
        ``POST /collections``

        Create a collection. This is used to create either a mapped or a guest
        collection. When created, a ``collection:administrator`` role for that
        collection will be created using the caller’s identity.

        In order to create a guest collection, the caller must have an identity that
        matches the Storage Gateway policies.

        In order to create a mapped collection, the caller must have an
        ``endpoint:administrator`` or ``endpoint:owner`` role.

        :param collection_data: The collection document for the new collection
        :type collection_data: dict or CollectionDocument
        """
        return UnpackingGCSResponse(
            self.post("/collections", data=collection_data), "collection"
        )

    @_gcsdoc("Update Collection", "openapi_Collections/#patchCollection")
    def update_collection(
        self,
        collection_id: UUIDLike,
        collection_data: Union[Dict[str, Any], CollectionDocument],
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        ``PATCH /collections/{collection_id}``

        :param collection_id: The ID of the collection to update
        :type collection_id: str or UUID
        :param collection_data: The collection document for the modified collection
        :type collection_data: dict or CollectionDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return UnpackingGCSResponse(
            self.patch(
                f"/collections/{collection_id}",
                data=collection_data,
                query_params=query_params,
            ),
            "collection",
        )

    @_gcsdoc("Delete Collection", "openapi_Collections/#deleteCollection")
    def delete_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /collections/{collection_id}``

        :param collection_id: The ID of the collection to delete
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.delete(f"/collections/{collection_id}", query_params=query_params)

    #
    # storage gateway methods
    #

    @_gcsdoc("List Storage Gateways", "openapi_Storage_Gateways/#getStorageGateways")
    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_storage_gateway_list(
        self,
        *,
        include: Union[None, str, Iterable[str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        ``GET /storage_gateways``

        :param include: Optional document types to include in the response. If
            'private_policies' is included, then include private storage gateway
            policies in the attached storage_gateways document. This requires an
            ``administrator`` role on the Endpoint.
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        return IterableGCSResponse(
            self.get("/storage_gateways", query_params=query_params)
        )

    @_gcsdoc("Create a Storage Gateway", "openapi_Storage_Gateways/#postStorageGateway")
    def create_storage_gateway(
        self,
        data: Union[Dict[str, Any], StorageGatewayDocument],
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        ``POST /storage_gateways``

        :param data: Data in the format of a Storage Gateway document, it is recommended
            to use the ``StorageGatewayDocumment`` class to construct this data.
        :type data: dict or StorageGatewayDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return UnpackingGCSResponse(
            self.post("/storage_gateways", data=data, query_params=query_params),
            "storage_gateway",
        )

    @_gcsdoc("Get a Storage Gateway", "openapi_Storage_Gateways/#getStorageGateway")
    def get_storage_gateway(
        self,
        storage_gateway_id: UUIDLike,
        *,
        include: Union[None, str, Iterable[str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        ``GET /storage_gateways/<storage_gateway_id>``

        :param storage_gateway_id: UUID for the Storage Gateway to be gotten
        :type storage_gateway_id: str or UUID
        :param include: Optional document types to include in the response. If
            'private_policies' is included, then include private storage gateway
            policies in the attached storage_gateways document. This requires an
            ``administrator`` role on the Endpoint.
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
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

    @_gcsdoc(
        "Update a Storage Gateway", "openapi_Storage_Gateways/#patchStorageGateway"
    )
    def update_storage_gateway(
        self,
        storage_gateway_id: UUIDLike,
        data: Union[Dict[str, Any], StorageGatewayDocument],
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``PATCH /storage_gateways/<storage_gateway_id>``

        :param storage_gateway_id: UUID for the Storage Gateway to be updated
        :type storage_gateway_id: str or UUID
        :param data: Data in the format of a Storage Gateway document, it is recommended
            to use the ``StorageGatewayDocumment`` class to construct this data.
        :type data: dict or StorageGatewayDocument
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.patch(
            f"/storage_gateways/{storage_gateway_id}",
            data=data,
            query_params=query_params,
        )

    @_gcsdoc(
        "Delete a Storage Gateway", "openapi_Storage_Gateways/#deleteStorageGateway"
    )
    def delete_storage_gateway(
        self,
        storage_gateway_id: Union[str, uuid.UUID],
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /storage_gateways/<storage_gateway_id>``

        :param storage_gateway_id: UUID for the Storage Gateway to be deleted
        :type storage_gateway_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.delete(
            f"/storage_gateways/{storage_gateway_id}", query_params=query_params
        )

    #
    # role methods
    #

    @_gcsdoc("List Roles", "openapi_Roles/#listRoles")
    @paging.has_paginator(
        paging.MarkerPaginator,
        items_key="data",
    )
    def get_role_list(
        self,
        collection_id: Optional[UUIDLike] = None,
        include: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        ``GET /roles``

        :param collection_id: UUID of a Collection. If given then only roles
            related to that Collection are returned, otherwise only Endpoint
            roles are returned.
        :type collection_id: str or UUID, optional
        :param include: Pass "all_roles" to request all roles all roles
            relevant to the resource instead of only those the caller has on
            the resource
        :type include: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = include
        if collection_id is not None:
            query_params["collection_id"] = collection_id

        path = "/roles"
        return IterableGCSResponse(self.get(path, query_params=query_params))

    @_gcsdoc("Create Role", "openapi_Roles/#postRole")
    def create_role(
        self,
        data: Union[Dict[str, Any], GCSRoleDocument],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        POST /roles

        :param data: Data in the format of a Role document, it is recommended
            to use the `GCSRoleDocumment` class to construct this data.
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = "/roles"
        return UnpackingGCSResponse(
            self.post(path, data=data, query_params=query_params),
            "role",
        )

    @_gcsdoc("Get a Role", "openapi_Roles/#getRole")
    def get_role(
        self,
        role_id: UUIDLike,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        GET /roles/{role_id}

        :param role_id: UUID for the Role to be gotten
        :type role_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = f"/roles/{role_id}"
        return UnpackingGCSResponse(self.get(path, query_params=query_params), "role")

    @_gcsdoc("Delete a Role", "openapi_Roles/#deleteRole")
    def delete_role(
        self,
        role_id: UUIDLike,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        DELETE /roles/{role_id}

        :param role_id: UUID for the Role to be deleted
        :type role_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = f"/roles/{role_id}"
        return self.delete(path, query_params=query_params)

    @_gcsdoc("Get User Credential list", "openapi_User_Credentials/#getUserCredentials")
    def get_user_credential_list(
        self,
        storage_gateway: Optional[UUIDLike] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        GET /user_credentials

        :param storage_gateway: UUID of a storage gateway to limit results to
        :type storage_gateway: str or UUID, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        if query_params is None:
            query_params = {}
        if storage_gateway is not None:
            query_params["storage_gateway"] = storage_gateway

        path = "/user_credentials"
        return IterableGCSResponse(self.get(path, query_params=query_params))

    @_gcsdoc("Create a User Credential", "openapi_User_Credentials/#postUserCredential")
    def create_user_credential(
        self,
        data: Union[Dict[str, Any], UserCredentialDocument],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        POST /user_credentials

        :param data: Data in the format of a UserCredential document, it is
            recommended to use the `UserCredential` class to construct this
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = "/user_credentials"
        return UnpackingGCSResponse(
            self.post(path, data=data, query_params=query_params),
            "user_credential",
        )

    @_gcsdoc("Get a User Credential", "openapi_User_Credentials/#getUserCredential")
    def get_user_credential(
        self,
        user_credential_id: UUIDLike,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        GET /user_credentials/{user_credential_id}

        :param user_credential_id: UUID for the UserCredential to be gotten
        :type user_credential_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = f"/user_credentials/{user_credential_id}"
        return UnpackingGCSResponse(
            self.get(path, query_params=query_params), "user_credential"
        )

    @_gcsdoc(
        "Update a User Credential", "openapi_User_Credentials/#patchUserCredential"
    )
    def update_user_credential(
        self,
        user_credential_id: UUIDLike,
        data: Union[Dict[str, Any], UserCredentialDocument],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        PATCH /user_credentials/{user_credential_id}

        :param user_credential_id: UUID for the UserCredential to be updated
        :type user_credential_id: str or UUID
        :param data: Data in the format of a UserCredential document, it is
            recommended to use the `UserCredential` class to construct this
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = f"/user_credentials/{user_credential_id}"
        return UnpackingGCSResponse(
            self.patch(path, data=data, query_params=query_params), "user_credential"
        )

    @_gcsdoc(
        "Delete a User Credential", "openapi_User_Credentials/#deleteUserCredential"
    )
    def delete_user_credential(
        self,
        user_credential_id: UUIDLike,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        DELETE /user_credentials/{user_credential_id}

        :param user_credential_id: UUID for the UserCredential to be deleted
        :type user_credential_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        path = f"/user_credentials/{user_credential_id}"
        return self.delete(path, query_params=query_params)
