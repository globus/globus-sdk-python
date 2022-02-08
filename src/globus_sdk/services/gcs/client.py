import uuid
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar, Union

from globus_sdk import client, paging, response, scopes, utils
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.types import UUIDLike

from .data import CollectionDocument, GCSRoleDocument
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

    @_gcsdoc("List Collections", "openapi_Collections/#ListCollections")
    def get_collection_list(
        self,
        *,
        include: Union[str, Iterable[str], None] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        ``GET /collections``

        :param include: Names of additional documents to include in the response
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        List the Collections on an Endpoint
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            if isinstance(include, str):
                include = [include]
            query_params["include"] = ",".join(include)
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
            query_params = {**query_params, "include": include}
        if collection_id is not None:
            query_params = {**query_params, "collection_id": collection_id}

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
            to use the `RoleDocumment` class to construct this data.
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
