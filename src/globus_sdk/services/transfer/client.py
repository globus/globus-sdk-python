from __future__ import annotations

import logging
import time
import typing as t
import uuid

from globus_sdk import client, exc, paging, response
from globus_sdk._types import DateLike, IntLike, UUIDLike
from globus_sdk.scopes import TransferScopes

from .data import DeleteData, TransferData
from .errors import TransferAPIError
from .response import ActivationRequirementsResponse, IterableTransferResponse
from .transport import TransferRequestsTransport

log = logging.getLogger(__name__)

TransferFilterDict = t.Dict[str, t.Union[str, t.List[str]]]


def _datelike_to_str(x: DateLike) -> str:
    return x if isinstance(x, str) else x.isoformat(timespec="seconds")


def _format_filter_value(x: str | list[str]) -> str:
    if isinstance(x, str):
        return x
    return ",".join(x)


def _format_filter_item(x: str | TransferFilterDict) -> str:
    if isinstance(x, str):
        return x
    return "/".join(f"{k}:{_format_filter_value(v)}" for k, v in x.items())


def _format_filter(
    x: (str | TransferFilterDict | list[str | TransferFilterDict]),
) -> str | list[str]:
    if isinstance(x, list):
        return [_format_filter_item(y) for y in x]
    return _format_filter_item(x)


def _get_page_size(paged_result: IterableTransferResponse) -> int:
    return len(paged_result["DATA"])


class TransferClient(client.BaseClient):
    r"""
    Client for the
    `Globus Transfer API <https://docs.globus.org/api/transfer/>`_.

    This class provides helper methods for most common resources in the
    REST API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base rest client that can be used to access any REST resource.

    Detailed documentation is available in the official REST API
    documentation, which is linked to from the method documentation. Methods
    that allow arbitrary keyword arguments will pass the extra arguments as
    query parameters.

    :param authorizer: An authorizer instance used for all calls to
                       Globus Transfer
    :type authorizer: :class:`GlobusAuthorizer\
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`

    .. _transfer_filter_formatting:

    **Filter Formatting**

    Several methods of ``TransferClient`` take a ``filter`` parameter which can be a
    string, dict, or list of strings/dicts. When the filter given is a string, it is
    passed as a single unmodified param. When the filter given is a dict, it is
    formatted according to the below rules into a single param. When the filter is a
    list, each item of the list is parsed and passed as separate params.

    dict parsing rules:
    - each (key, value) pair in the dict is a clause in the resulting filter string
    - clauses are each formatted to ``key:value``
    - when the value is a list, it is comma-separated, as in ``key:value1,value2``
    - clauses are separated with slashes, as in ``key1:value1/key2:value2``

    The corresponding external API documentation describes, in detail, the supported
    filter clauses for each method which uses the ``filter`` parameter.
    Generally, speaking, filter clauses documented as ``string list`` can be passed as
    lists to a filter dict, while string, date, and numeric filters should be passed as
    strings.

    **Paginated Calls**

    Methods which support pagination can be called as paginated or unpaginated methods.
    If the method name is ``TransferClient.foo``, the paginated version is
    ``TransferClient.paginated.foo``.
    Using ``TransferClient.endpoint_search`` as an example::

        from globus_sdk import TransferClient
        tc = TransferClient(...)

        # this is the unpaginated version
        for x in tc.endpoint_search("tutorial"):
            print("Endpoint ID: {}".format(x["id"]))

        # this is the paginated version
        for page in tc.paginated.endpoint_search("testdata"):
            for x in page:
                print("Endpoint ID: {}".format(x["id"]))

    .. automethodlist:: globus_sdk.TransferClient
    """
    service_name = "transfer"
    base_path = "/v0.10/"
    transport_class: type[TransferRequestsTransport] = TransferRequestsTransport
    error_class = TransferAPIError
    scopes = TransferScopes

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

    def get_endpoint(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: ID of endpoint to lookup
        :type endpoint_id: str or UUID
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    endpoint = tc.get_endpoint(endpoint_id)
                    print("Endpoint name:", endpoint["display_name"] or endpoint["canonical_name"])

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>``

                .. extdoclink:: Get Endpoint by ID
                    :ref: transfer/endpoint/#get_endpoint_by_id
        """  # noqa: E501
        log.info(f"TransferClient.get_endpoint({endpoint_id})")
        return self.get(f"endpoint/{endpoint_id}", query_params=query_params)

    def update_endpoint(
        self,
        endpoint_id: UUIDLike,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: ID of endpoint to lookup
        :type endpoint_id: str or UUID
        :param data: A partial endpoint document with fields to update
        :type data: dict
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    epup = {
                        "display_name": "My New Endpoint Name",
                        "description": "Better Description",
                    }
                    update_result = tc.update_endpoint(endpoint_id, epup)

            .. tab-item:: API Info

                ``PUT /endpoint/<endpoint_id>``

                .. extdoclink:: Update Endpoint by ID
                    :ref: transfer/endpoint/#update_endpoint_by_id
        """  # noqa: E501
        if data.get("myproxy_server"):
            if data.get("oauth_server"):
                raise exc.GlobusSDKUsageError(
                    "an endpoint cannot be reconfigured to use multiple "
                    "identity providers for activation; specify either "
                    "MyProxy or OAuth, not both"
                )
            else:
                data["oauth_server"] = None
        elif data.get("oauth_server"):
            data["myproxy_server"] = None

        log.info(f"TransferClient.update_endpoint({endpoint_id}, ...)")
        return self.put(f"endpoint/{endpoint_id}", data=data, query_params=query_params)

    def create_endpoint(self, data: dict[str, t.Any]) -> response.GlobusHTTPResponse:
        """
        :param data: An endpoint document with fields for the new endpoint
        :type data: dict

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    ep_data = {
                        "DATA_TYPE": "endpoint",
                        "display_name": display_name,
                        "DATA": [
                            {
                                "DATA_TYPE": "server",
                                "hostname": "gridftp.example.edu",
                            },
                        ],
                    }
                    create_result = tc.create_endpoint(ep_data)
                    endpoint_id = create_result["id"]

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>``

                .. extdoclink:: Create Endpoint
                    :ref: transfer/endpoint/#create_endpoint
        """
        if data.get("myproxy_server") and data.get("oauth_server"):
            raise exc.GlobusSDKUsageError(
                "an endpoint cannot be created using multiple identity "
                "providers for activation; specify either MyProxy or OAuth, "
                "not both"
            )

        log.info("TransferClient.create_endpoint(...)")
        return self.post("endpoint", data=data)

    def delete_endpoint(self, endpoint_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: ID of endpoint to delete
        :type endpoint_id: str or UUID

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    delete_result = tc.delete_endpoint(endpoint_id)

            .. tab-item:: API Info

                ``DELETE /endpoint/<endpoint_id>``

                .. extdoclink:: Delete Endpoint by ID
                    :ref: transfer/endpoint/#delete_endpoint_by_id
        """
        log.info(f"TransferClient.delete_endpoint({endpoint_id})")
        return self.delete(f"endpoint/{endpoint_id}")

    @paging.has_paginator(
        paging.HasNextPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=100,
    )
    def endpoint_search(
        self,
        filter_fulltext: str | None = None,
        *,
        filter_scope: str | None = None,
        filter_owner_id: str | None = None,
        filter_host_endpoint: UUIDLike | None = None,
        filter_non_functional: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        r"""
        :param filter_fulltext: The string to use in a full text search on endpoints.
            Effectively, the "search query" which is being requested. May be omitted
            with specific ``filter_scope`` values.
        :type filter_fulltext: str, optional
        :param filter_scope: A "scope" within which to search for endpoints. This must
            be one of the limited and known names known to the service, which can be
            found documented in the **External Documentation** below. Defaults to
            searching all endpoints (in which case ``filter_fulltext`` is required)
        :type filter_scope: str, optional
        :param filter_owner_id: Limit search to endpoints owned by the specified Globus
            Auth identity. Conflicts with scopes 'my-endpoints', 'my-gcp-endpoints', and
            'shared-by-me'.
        :type filter_owner_id: str, optional
        :param filter_host_endpoint: Limit search to endpoints hosted by the specified
            endpoint. May cause BadRequest or PermissionDenied errors if the endpoint ID
            given is not valid for this operation.
        :type filter_host_endpoint: str, optional
        :param filter_non_functional: Limit search to endpoints which have the
            'non_functional' flag set to True or False.
        :type filter_non_functional: bool, optional
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        It is important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query.

        .. tab-set::

            .. tab-item:: Example Usage

                Search for a given string as a fulltext search:

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    for ep in tc.endpoint_search("String to search for!"):
                        print(ep["display_name"])

                Search for a given string, but only on endpoints that you own:

                .. code-block:: python

                    for ep in tc.endpoint_search("foo", filter_scope="my-endpoints"):
                        print(f"{ep['display_name']} has ID {ep['id']}")

            .. tab-item:: Paginated Usage

                .. paginatedusage:: endpoint_search

            .. tab-item:: API Info

                .. parsed-literal::

                    GET /endpoint_search\
                    ?filter_fulltext=<filter_fulltext>&filter_scope=<filter_scope>

                .. extdoclink:: Endpoint Search
                    :ref: transfer/endpoint_search
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        if filter_scope is not None:
            query_params["filter_scope"] = filter_scope
        if filter_fulltext is not None:
            query_params["filter_fulltext"] = filter_fulltext
        if filter_owner_id is not None:
            query_params["filter_owner_id"] = filter_owner_id
        if filter_host_endpoint is not None:  # convert to str (may be UUID)
            query_params["filter_host_endpoint"] = str(filter_host_endpoint)
        if filter_non_functional is not None:  # convert to int (expect bool input)
            query_params["filter_non_functional"] = 1 if filter_non_functional else 0
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        log.info(f"TransferClient.endpoint_search({query_params})")
        return IterableTransferResponse(
            self.get("endpoint_search", query_params=query_params)
        )

    def endpoint_autoactivate(
        self,
        endpoint_id: UUIDLike,
        *,
        if_expires_in: int | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        r"""
        :param endpoint_id: The ID of the endpoint to autoactivate
        :type endpoint_id: str or UUID
        :param if_expires_in: A number of seconds. Autoactivation will only be attempted
            if the current activation expires within this timeframe. Otherwise,
            autoactivation will succeed with a code of 'AlreadyActivated'
        :type if_expires_in: int, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        The following example will try to "auto" activate the endpoint
        using a credential available from another endpoint or sign in by
        the user with the same identity provider, but only if the
        endpoint is not already activated or going to expire within an
        hour (3600 seconds). If that fails, direct the user to the
        globus website to perform activation:

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
                    while r["code"] == "AutoActivationFailed":
                        print(
                            "Endpoint requires manual activation, please open "
                            "the following URL in a browser to activate the endpoint: "
                            f"https://app.globus.org/file-manager?origin_id={ep_id}"
                        )
                        input("Press ENTER after activating the endpoint:")
                        r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)

                This is the recommended flow for most thick client applications,
                because many endpoints require activation via OAuth MyProxy,
                which must be done in a browser anyway. Web based clients can
                link directly to the URL.

                You also might want messaging or logging depending on why and how the
                operation succeeded, in which case you'll need to look at the value of
                the "code" field and either decide on your own messaging or use the
                response's "message" field.

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
                    if r["code"] == "AutoActivationFailed":
                        print(f"Endpoint({ep_id}) Not Active! Error! Source message: {r['message']}")
                        sys.exit(1)
                    elif r["code"] == "AutoActivated.CachedCredential":
                        print(f"Endpoint({ep_id}) autoactivated using a cached credential.")
                    elif r["code"] == "AutoActivated.GlobusOnlineCredential":
                        print(f"Endpoint({ep_id}) autoactivated using a built-in Globus credential.")
                    elif r["code"] == "AlreadyActivated":
                        print(f"Endpoint({ep_id}) already active for at least 3600 seconds")

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/autoactivate``

                .. extdoclink:: Autoactivate Endpoint
                    :ref: transfer/endpoint_activation/#autoactivate_endpoint
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        if if_expires_in is not None:
            query_params["if_expires_in"] = if_expires_in
        log.info(f"TransferClient.endpoint_autoactivate({endpoint_id})")
        return self.post(
            f"endpoint/{endpoint_id}/autoactivate", query_params=query_params
        )

    def endpoint_deactivate(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The ID of the endpoint to deactivate
        :type endpoint_id: str or UUID
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/deactivate``

                .. extdoclink:: Deactivate Endpoint
                    :ref: transfer/endpoint_activation/#deactivate_endpoint
        """
        log.info(f"TransferClient.endpoint_deactivate({endpoint_id})")
        return self.post(
            f"endpoint/{endpoint_id}/deactivate", query_params=query_params
        )

    def endpoint_activate(
        self,
        endpoint_id: UUIDLike,
        *,
        requirements_data: dict[str, t.Any] | None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The ID of the endpoint to activate
        :type endpoint_id: str or UUID
        :pram requirements_data: Filled in activation requirements data, as can be
            fetched from :meth:`~endpoint_get_activation_requirements`. Only the fields
            for the activation type being used need to be filled in.
        :type requirements_data: dict
        :param requirements_data: An optional body for the request
        :type requirements_data: dict, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        Consider using autoactivate and web activation instead, described
        in the example for :meth:`~endpoint_autoactivate`.

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/activate``

                .. extdoclink:: Activate Endpoint
                    :ref: transfer/endpoint_activation/#activate_endpoint
        """
        log.info(f"TransferClient.endpoint_activate({endpoint_id})")
        return self.post(
            f"endpoint/{endpoint_id}/activate",
            data=requirements_data,
            query_params=query_params,
        )

    def endpoint_get_activation_requirements(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> ActivationRequirementsResponse:
        """
        :param endpoint_id: The ID of the endpoint whose activation requirements data is
            being looked up
        :type endpoint_id: str or UUID
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/activation_requirements``

                .. extdoclink:: Get Activation Requirements
                    :ref: transfer/endpoint_activation/#get_activation_requirements
        """
        return ActivationRequirementsResponse(
            self.get(
                f"endpoint/{endpoint_id}/activation_requirements",
                query_params=query_params,
            )
        )

    def my_effective_pause_rule_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: the endpoint on which the current user's effective pause
            rules are fetched
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/my_effective_pause_rule_list``

                .. extdoclink:: Get my effective endpoint pause rules
                    :ref: transfer/endpoint/#get_endpoint_pause_rules
        """
        log.info(f"TransferClient.my_effective_pause_rule_list({endpoint_id}, ...)")
        return IterableTransferResponse(
            self.get(
                f"endpoint/{endpoint_id}/my_effective_pause_rule_list",
                query_params=query_params,
            )
        )

    # Shared Endpoints

    def my_shared_endpoint_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: the host endpoint whose shares are listed
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        Get a list of shared endpoints for which the user has ``administrator`` or
        ``access_manager`` on a given host endpoint.

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/my_shared_endpoint_list``

                .. extdoclink:: Get shared endpoint list
                    :ref: transfer/endpoint/#get_shared_endpoint_list
        """
        log.info(f"TransferClient.my_shared_endpoint_list({endpoint_id}, ...)")
        return IterableTransferResponse(
            self.get(
                f"endpoint/{endpoint_id}/my_shared_endpoint_list",
                query_params=query_params,
            )
        )

    @paging.has_paginator(paging.NextTokenPaginator, items_key="shared_endpoints")
    def get_shared_endpoint_list(
        self,
        endpoint_id: UUIDLike,
        *,
        max_results: int | None = None,
        next_token: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: the host endpoint whose shares are listed
        :type endpoint_id: str or UUID
        :param max_results: cap to the number of results
        :type max_results: int, optional
        :param next_token: token used for paging
        :type next_token: str, optional
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        Get a list of all shared endpoints on a given host endpoint.

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: get_shared_endpoint_list

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/shared_endpoint_list``

                .. extdoclink:: Get shared endpoint list (2)
                    :ref: transfer/endpoint/#get_shared_endpoint_list2
        """
        log.info(f"TransferClient.get_shared_endpoint_list({endpoint_id}, ...)")
        if query_params is None:
            query_params = {}
        if max_results is not None:
            query_params["max_results"] = str(max_results)
        if next_token is not None:
            query_params["next_token"] = str(next_token)
        return IterableTransferResponse(
            self.get(
                f"endpoint/{endpoint_id}/shared_endpoint_list",
                query_params=query_params,
            ),
            iter_key="shared_endpoints",
        )

    def create_shared_endpoint(
        self, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param data: A python dict representation of a ``shared_endpoint`` document
        :type data: dict

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    shared_ep_data = {
                        "DATA_TYPE": "shared_endpoint",
                        "host_endpoint": host_endpoint_id,
                        "host_path": host_path,
                        "display_name": display_name,
                        # optionally specify additional endpoint fields
                        "description": "my test share",
                    }
                    create_result = tc.create_shared_endpoint(shared_ep_data)
                    endpoint_id = create_result["id"]

            .. tab-item:: API Info

                ``POST /shared_endpoint``

                .. extdoclink:: Create Shared Endpoint
                    :ref: transfer/endpoint/#create_shared_endpoint
        """
        log.info("TransferClient.create_shared_endpoint(...)")
        return self.post("shared_endpoint", data=data)

    # Endpoint servers

    def endpoint_server_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: The endpoint whose servers are being listed
        :type endpoint_id: str or UUID
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/server_list``

                .. extdoclink:: Get endpoint server list
                    :ref: transfer/endpoint/#get_endpoint_server_list
        """
        log.info(f"TransferClient.endpoint_server_list({endpoint_id}, ...)")
        return IterableTransferResponse(
            self.get(f"endpoint/{endpoint_id}/server_list", query_params=query_params)
        )

    def get_endpoint_server(
        self,
        endpoint_id: UUIDLike,
        server_id: IntLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint under which the server is registered
        :type endpoint_id: str or UUID
        :param server_id: The ID of the server
        :type server_id: str or int
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/server/<server_id>``

                .. extdoclink:: Get endpoint server by id
                    :ref: transfer/endpoint/#get_endpoint_server_by_id
        """
        log.info(
            "TransferClient.get_endpoint_server(%s, %s, ...)", endpoint_id, server_id
        )
        return self.get(
            f"endpoint/{endpoint_id}/server/{server_id}", query_params=query_params
        )

    def add_endpoint_server(
        self, endpoint_id: UUIDLike, server_data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint under which the server is being registered
        :type endpoint_id: str or UUID
        :param server_data: Fields for the new server, as a server document
        :type server_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/server``

                .. extdoclink:: Add endpoint server
                    :ref: transfer/endpoint/#add_endpoint_server
        """
        log.info(f"TransferClient.add_endpoint_server({endpoint_id}, ...)")
        return self.post(f"endpoint/{endpoint_id}/server", data=server_data)

    def update_endpoint_server(
        self,
        endpoint_id: UUIDLike,
        server_id: IntLike,
        server_data: dict[str, t.Any],
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint under which the server is registered
        :type endpoint_id: str or UUID
        :param server_id: The ID of the server to update
        :type server_id: str or int
        :param server_data: Fields on the server to update, as a partial server document
        :type server_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /endpoint/<endpoint_id>/server/<server_id>``

                .. extdoclink:: Update endpoint server by ID
                    :ref: transfer/endpoint/#update_endpoint_server_by_id
        """
        log.info(
            "TransferClient.update_endpoint_server(%s, %s, ...)",
            endpoint_id,
            server_id,
        )
        return self.put(f"endpoint/{endpoint_id}/server/{server_id}", data=server_data)

    def delete_endpoint_server(
        self, endpoint_id: UUIDLike, server_id: IntLike
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint under which the server is registered
        :type endpoint_id: str or UUID
        :param server_id: The ID of the server to delete
        :type server_id: str or int

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /endpoint/<endpoint_id>/server/<server_id>``

                .. extdoclink:: Delete endpoint server by ID
                    :ref: transfer/endpoint/#delete_endpoint_server_by_id
        """
        log.info(
            "TransferClient.delete_endpoint_server(%s, %s)", endpoint_id, server_id
        )
        return self.delete(f"endpoint/{endpoint_id}/server/{server_id}")

    #
    # Roles
    #

    def endpoint_role_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: The endpoint whose roles are being listed
        :type endpoint_id: str or UUID
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/role_list``

                .. extdoclink:: Get list of endpoint roles
                    :ref: transfer/endpoint_roles/#role_list
        """
        log.info(f"TransferClient.endpoint_role_list({endpoint_id}, ...)")
        return IterableTransferResponse(
            self.get(f"endpoint/{endpoint_id}/role_list", query_params=query_params)
        )

    def add_endpoint_role(
        self, endpoint_id: UUIDLike, role_data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the role is being added
        :type endpoint_id: str or UUID
        :param role_data: A role document for the new role
        :type role_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/role``

                .. extdoclink:: Create endpoint role
                    :ref: transfer/endpoint_roles/#create_role
        """
        log.info(f"TransferClient.add_endpoint_role({endpoint_id}, ...)")
        return self.post(f"endpoint/{endpoint_id}/role", data=role_data)

    def get_endpoint_role(
        self,
        endpoint_id: UUIDLike,
        role_id: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the role applies
        :type endpoint_id: str or UUID
        :param role_id: The ID of the role
        :type role_id: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/role/<role_id>``

                .. extdoclink:: Get endpoint role by ID
                    :ref: transfer/endpoint_roles/#get_endpoint_role_by_id
        """
        log.info(f"TransferClient.get_endpoint_role({endpoint_id}, {role_id}, ...)")
        return self.get(
            f"endpoint/{endpoint_id}/role/{role_id}", query_params=query_params
        )

    def delete_endpoint_role(
        self, endpoint_id: UUIDLike, role_id: str
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the role applies
        :type endpoint_id: str or UUID
        :param role_id: The ID of the role to delete
        :type role_id: str

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /endpoint/<endpoint_id>/role/<role_id>``

                .. extdoclink:: Delete endpoint role by ID
                    :ref: transfer/endpoint_roles/#delete_endpoint_role_by_id
        """
        log.info(f"TransferClient.delete_endpoint_role({endpoint_id}, {role_id})")
        return self.delete(f"endpoint/{endpoint_id}/role/{role_id}")

    #
    # ACLs
    #

    def endpoint_acl_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: The endpoint whose ACLs are being listed
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/access_list``

                .. extdoclink:: Get list of access rules
                    :ref: transfer/acl/#rest_access_get_list
        """
        log.info(f"TransferClient.endpoint_acl_list({endpoint_id}, ...)")
        return IterableTransferResponse(
            self.get(f"endpoint/{endpoint_id}/access_list", query_params=query_params)
        )

    def get_endpoint_acl_rule(
        self,
        endpoint_id: UUIDLike,
        rule_id: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the access rule applies
        :type endpoint_id: str or UUID
        :param rule_id: The ID of the rule to fetch
        :type rule_id: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint/<endpoint_id>/access/<rule_id>``

                .. extdoclink:: Get access rule by ID
                    :ref: transfer/acl/#get_access_rule_by_id
        """
        log.info(
            "TransferClient.get_endpoint_acl_rule(%s, %s, ...)", endpoint_id, rule_id
        )
        return self.get(
            f"endpoint/{endpoint_id}/access/{rule_id}", query_params=query_params
        )

    def add_endpoint_acl_rule(
        self, endpoint_id: UUIDLike, rule_data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: ID of endpoint to which to add the acl
        :type endpoint_id: str
        :param rule_data: A python dict representation of an ``access`` document
        :type rule_data: dict

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    rule_data = {
                        "DATA_TYPE": "access",
                        "principal_type": "identity",
                        "principal": identity_id,
                        "path": "/dataset1/",
                        "permissions": "rw",
                    }
                    result = tc.add_endpoint_acl_rule(endpoint_id, rule_data)
                    rule_id = result["access_id"]

                Note that if this rule is being created on a shared endpoint
                the "path" field is relative to the "host_path" of the shared endpoint.

            .. tab-item:: API Info

                ``POST /endpoint/<endpoint_id>/access``

                .. extdoclink:: Create access rule
                    :ref: transfer/acl/#rest_access_create
        """
        log.info(f"TransferClient.add_endpoint_acl_rule({endpoint_id}, ...)")
        return self.post(f"endpoint/{endpoint_id}/access", data=rule_data)

    def update_endpoint_acl_rule(
        self,
        endpoint_id: UUIDLike,
        rule_id: str,
        rule_data: dict[str, t.Any],
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the access rule applies
        :type endpoint_id: str or UUID
        :param rule_id: The ID of the access rule to modify
        :type rule_id: str
        :param rule_data: A partial ``access`` document containing fields to update
        :type rule_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /endpoint/<endpoint_id>/access/<rule_id>``

                .. extdoclink:: Update access rule
                    :ref: transfer/acl/#update_access_rule
        """
        log.info(
            "TransferClient.update_endpoint_acl_rule(%s, %s, ...)",
            endpoint_id,
            rule_id,
        )
        return self.put(f"endpoint/{endpoint_id}/access/{rule_id}", data=rule_data)

    def delete_endpoint_acl_rule(
        self, endpoint_id: UUIDLike, rule_id: str
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The endpoint on which the access rule applies
        :type endpoint_id: str or UUID
        :param rule_id: The ID of the access rule to remove
        :type rule_id: str

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /endpoint/<endpoint_id>/access/<rule_id>``

                .. extdoclink:: Delete access rule
                    :ref: transfer/acl/#delete_access_rule
        """
        log.info(
            "TransferClient.delete_endpoint_acl_rule(%s, %s)", endpoint_id, rule_id
        )
        return self.delete(f"endpoint/{endpoint_id}/access/{rule_id}")

    #
    # Bookmarks
    #

    def bookmark_list(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> IterableTransferResponse:
        """
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /bookmark_list``

                .. extdoclink:: Get list of bookmarks
                    :ref: transfer/endpoint_bookmarks/#get_list_of_bookmarks
        """
        log.info(f"TransferClient.bookmark_list({query_params})")
        return IterableTransferResponse(
            self.get("bookmark_list", query_params=query_params)
        )

    def create_bookmark(
        self, bookmark_data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param bookmark_data: A bookmark document for the bookmark to create
        :type bookmark_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``POST /bookmark``

                .. extdoclink:: Create bookmark
                    :ref: transfer/endpoint_bookmarks/#create_bookmark
        """
        log.info(f"TransferClient.create_bookmark({bookmark_data})")
        return self.post("bookmark", data=bookmark_data)

    def get_bookmark(
        self,
        bookmark_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param bookmark_id: The ID of the bookmark to lookup
        :type bookmark_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /bookmark/<bookmark_id>``

                .. extdoclink:: Get bookmark by ID
                    :ref: transfer/endpoint_bookmarks/#get_bookmark_by_id
        """
        log.info(f"TransferClient.get_bookmark({bookmark_id})")
        return self.get(f"bookmark/{bookmark_id}", query_params=query_params)

    def update_bookmark(
        self, bookmark_id: UUIDLike, bookmark_data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        :param bookmark_id: The ID of the bookmark to modify
        :type bookmark_id: str or UUID
        :param bookmark_data: A partial bookmark document with fields to update
        :type bookmark_data: dict

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /bookmark/<bookmark_id>``

                .. extdoclink:: Update bookmark
                    :ref: transfer/endpoint_bookmarks/#update_bookmark
        """
        log.info(f"TransferClient.update_bookmark({bookmark_id})")
        return self.put(f"bookmark/{bookmark_id}", data=bookmark_data)

    def delete_bookmark(self, bookmark_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        :param bookmark_id: The ID of the bookmark to delete
        :type bookmark_id: str or UUID

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /bookmark/<bookmark_id>``

                .. extdoclink:: Delete bookmark by ID
                    :ref: transfer/endpoint_bookmarks/#delete_bookmark_by_id
        """
        log.info(f"TransferClient.delete_bookmark({bookmark_id})")
        return self.delete(f"bookmark/{bookmark_id}")

    #
    # Synchronous Filesys Operations
    #

    def operation_ls(
        self,
        endpoint_id: UUIDLike,
        path: str | None = None,
        *,
        show_hidden: bool | None = None,
        orderby: str | list[str] | None = None,
        # note: filter is a soft keyword in python, so using this name is okay
        # pylint: disable=redefined-builtin
        filter: (
            str | TransferFilterDict | list[str | TransferFilterDict] | None
        ) = None,
        local_user: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        :param endpoint_id: The ID of the endpoint on which to do a dir listing
        :type endpoint_id: str or UUID
        :param path: Path to a directory on the endpoint to list
        :type path: str, optional
        :param show_hidden: Show hidden files (names beginning in dot).
            Defaults to true.
        :type show_hidden: bool, optional
        :param orderby: One or more order-by options. Each option is
            either a field name or a field name followed by a space and 'ASC' or 'DESC'
            for ascending or descending.
        :type orderby: str, optional
        :param filter: Only return file documents which match these filter clauses. For
            the filter syntax, see the **External Documentation** linked below. If a
            dict is supplied as the filter, it is formatted as a set of filter clauses.
            If a list is supplied, it is passed as multiple params.
            See :ref:`filter formatting <transfer_filter_formatting>` for details.
        :type filter: str or dict, optional
        :param local_user: Optional value passed to identity mapping specifying which
            local user account to map to. Only usable with Globus Connect Server v5
            mapped collections.
        :type local_user: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                List with a path:

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    for entry in tc.operation_ls(ep_id, path="/~/project1/"):
                        print(entry["name"], entry["type"])

                List with explicit ordering:

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    for entry in tc.operation_ls(ep_id, path="/~/project1/", orderby=["type", "name"]):
                        print(entry["name DESC"], entry["type"])

                List filtering to files modified before January 1, 2021. Note the use
                of an empty "start date" for the filter:

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    for entry in tc.operation_ls(
                        ep_id,
                        path="/~/project1/",
                        filter={"last_modified": ["", "2021-01-01"]},
                    ):
                        print(entry["name"], entry["type"])

            .. tab-item:: API Info

                ``GET /operation/endpoint/<endpoint_id>/ls``

                .. extdoclink:: List Directory Contents
                    :ref: transfer/file_operations/#list_directory_contents
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        if path is not None:
            query_params["path"] = path
        if show_hidden is not None:
            query_params["show_hidden"] = 1 if show_hidden else 0
        if orderby is not None:
            if isinstance(orderby, str):
                query_params["orderby"] = orderby
            else:
                query_params["orderby"] = ",".join(orderby)
        if filter is not None:
            query_params["filter"] = _format_filter(filter)
        if local_user is not None:
            query_params["local_user"] = local_user

        log.info(f"TransferClient.operation_ls({endpoint_id}, {query_params})")
        return IterableTransferResponse(
            self.get(f"operation/endpoint/{endpoint_id}/ls", query_params=query_params)
        )

    def operation_mkdir(
        self,
        endpoint_id: UUIDLike,
        path: str,
        *,
        local_user: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The ID of the endpoint on which to create a directory
        :type endpoint_id: str or UUID
        :param path: Path to the new directory to create
        :type path: str
        :param local_user: Optional value passed to identity mapping specifying which
            local user account to map to. Only usable with Globus Connect Server v5
            mapped collections.
        :type local_user: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    tc.operation_mkdir(ep_id, path="/~/newdir/")

            .. tab-item:: API Info

                ``POST /operation/endpoint/<endpoint_id>/mkdir``

                .. extdoclink:: Make Directory
                    :ref: transfer/file_operations/#make_directory
        """
        log.info(
            "TransferClient.operation_mkdir({}, {}, {})".format(
                endpoint_id, path, query_params
            )
        )
        json_body = {"DATA_TYPE": "mkdir", "path": path}
        if local_user is not None:
            json_body["local_user"] = local_user
        return self.post(
            f"operation/endpoint/{endpoint_id}/mkdir",
            data=json_body,
            query_params=query_params,
        )

    def operation_rename(
        self,
        endpoint_id: UUIDLike,
        oldpath: str,
        newpath: str,
        *,
        local_user: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The ID of the endpoint on which to rename a file
        :type endpoint_id: str or UUID
        :param oldpath: Path to the old filename
        :type oldpath: str
        :param newpath: Path to the new filename
        :type newpath: str
        :param local_user: Optional value passed to identity mapping specifying which
            local user account to map to. Only usable with Globus Connect Server v5
            mapped collections.
        :type local_user: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    tc.operation_rename(ep_id, oldpath="/~/file1.txt", newpath="/~/project1data.txt")

            .. tab-item:: API Info

                ``POST /operation/endpoint/<endpoint_id>/rename``

                .. extdoclink:: Rename
                    :ref: transfer/file_operations/#rename
        """  # noqa: E501
        log.info(
            "TransferClient.operation_rename({}, {}, {}, {})".format(
                endpoint_id, oldpath, newpath, query_params
            )
        )
        json_body = {
            "DATA_TYPE": "rename",
            "old_path": oldpath,
            "new_path": newpath,
        }
        if local_user is not None:
            json_body["local_user"] = local_user
        return self.post(
            f"operation/endpoint/{endpoint_id}/rename",
            data=json_body,
            query_params=query_params,
        )

    def operation_symlink(
        self,
        endpoint_id: UUIDLike,
        symlink_target: str,
        path: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param endpoint_id: The ID of the endpoint on which to create a symlink
        :type endpoint_id: str or UUID
        :param symlink_target: The path referenced by the new symlink
        :type symlink_target: str
        :param path: The name of (path to) the new symlink
        :type path: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    tc.operation_symlink(ep_id, symlink_target="/~/file1.txt", path="/~/link-to-file1.txt")

            .. tab-item:: API Info

                ``POST /operation/endpoint/<endpoint_id>/symlink``

                .. extdoclink:: Symlink
                    :ref: transfer/file_operations/#symlink
        """  # noqa: E501
        log.info(
            "TransferClient.operation_symlink({}, {}, {}, {})".format(
                endpoint_id, symlink_target, path, query_params
            )
        )
        data = {
            "DATA_TYPE": "symlink",
            "symlink_target": symlink_target,
            "path": path,
        }
        return self.post(
            f"operation/endpoint/{endpoint_id}/symlink",
            data=data,
            query_params=query_params,
        )

    #
    # Task Submission
    #

    def get_submission_id(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.GlobusHTTPResponse:
        """
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        Submission IDs are required to submit tasks to the Transfer service
        via the :meth:`submit_transfer <.submit_transfer>` and
        :meth:`submit_delete <.submit_delete>` methods.

        Most users will not need to call this method directly, as the
        methods :meth:`~submit_transfer` and :meth:`~submit_delete` will call it
        automatically if the data does not contain a ``submission_id``.

        .. tab-set::

            .. tab-item:: API Info

                ``GET /submission_id``

                .. extdoclink:: Get a submission ID
                    :ref: transfer/task_submit/#get_submission_id

            .. tab-item:: Example Response Data

                .. expandtestfixture:: transfer.get_submission_id
        """
        log.info(f"TransferClient.get_submission_id({query_params})")
        return self.get("submission_id", query_params=query_params)

    def submit_transfer(
        self, data: dict[str, t.Any] | TransferData
    ) -> response.GlobusHTTPResponse:
        """
        :param data: A transfer task document listing files and directories, and setting
            various options. See :class:`TransferData <globus_sdk.TransferData>` for
            details
        :type data: dict or TransferData

        Submit a Transfer Task.

        If no ``submission_id`` is included in the payload, one will be requested and
        used automatically. The data passed to this method will be modified to include
        the ``submission_id``.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    tdata = globus_sdk.TransferData(
                        tc,
                        source_endpoint_id,
                        destination_endpoint_id,
                        label="SDK example",
                        sync_level="checksum",
                    )
                    tdata.add_item("/source/path/dir/", "/dest/path/dir/", recursive=True)
                    tdata.add_item("/source/path/file.txt", "/dest/path/file.txt")
                    transfer_result = tc.submit_transfer(tdata)
                    print("task_id =", transfer_result["task_id"])

                The `data` parameter can be a normal Python dictionary, or
                a :class:`TransferData <globus_sdk.TransferData>` object.

            .. tab-item:: API Info

                ``POST /transfer``

                .. extdoclink:: Submit a transfer task
                    :ref: transfer/task_submit/#submit_transfer_task
        """  # noqa: E501
        log.info("TransferClient.submit_transfer(...)")
        if "submission_id" not in data:
            log.debug("submit_transfer autofetching submission_id")
            data["submission_id"] = self.get_submission_id()["value"]
        return self.post("/transfer", data=data)

    def submit_delete(
        self, data: dict[str, t.Any] | DeleteData
    ) -> response.GlobusHTTPResponse:
        """
        :param data: A delete task document listing files and directories, and setting
            various options. See :class:`DeleteData <globus_sdk.DeleteData>` for
            details
        :type data: dict or DeleteData

        Submit a Delete Task.

        If no ``submission_id`` is included in the payload, one will be requested and
        used automatically. The data passed to this method will be modified to include
        the ``submission_id``.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    ddata = globus_sdk.DeleteData(tc, endpoint_id, recursive=True)
                    ddata.add_item("/dir/to/delete/")
                    ddata.add_item("/file/to/delete/file.txt")
                    delete_result = tc.submit_delete(ddata)
                    print("task_id =", delete_result["task_id"])

                The `data` parameter can be a normal Python dictionary, or
                a :class:`DeleteData <globus_sdk.DeleteData>` object.

            .. tab-item:: API Info

                ``POST /delete``

                .. extdoclink:: Submit a delete task
                    :ref: transfer/task_submit/#submit_delete_task
        """
        log.info("TransferClient.submit_delete(...)")
        if "submission_id" not in data:
            log.debug("submit_delete autofetching submission_id")
            data["submission_id"] = self.get_submission_id()["value"]
        return self.post("/delete", data=data)

    #
    # Task inspection and management
    #

    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def task_list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        # pylint: disable=redefined-builtin
        filter: str | TransferFilterDict | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get an iterable of task documents owned by the current user.

        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param filter: Only return task documents which match these filter clauses. For
            the filter syntax, see the **External Documentation** linked below. If a
            dict is supplied as the filter, it is formatted as a set of filter clauses.
            See :ref:`filter formatting <transfer_filter_formatting>` for details.
        :type filter: str or dict, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch 10 tasks and print some basic info:

                .. code-block:: python

                    tc = TransferClient(...)
                    for task in tc.task_list(limit=10):
                        print(
                            f"Task({task['task_id']}): "
                            f"{task['source_endpoint']} -> {task['destination_endpoint']}"
                        )

                Fetch 3 *specific* tasks using a ``task_id`` filter:

                .. code-block:: python

                    tc = TransferClient(...)
                    task_ids = [
                        "acb4b581-b3f3-403a-a42a-9da97aaa9961",
                        "39447a3c-e002-401a-b95c-f48b69b4c60a",
                        "02330d3a-987b-4abb-97ed-6a22f8fa365e",
                    ]
                    for task in tc.task_list(filter={"task_id": task_ids}):
                        print(
                            f"Task({task['task_id']}): "
                            f"{task['source_endpoint']} -> {task['destination_endpoint']}"
                        )

            .. tab-item:: Paginated Usage

                .. paginatedusage:: task_list

            .. tab-item:: API Info

                ``GET /task_list``

                .. extdoclink:: Task List
                    :ref: transfer/task/#get_task_list
        """  # noqa: E501
        log.info("TransferClient.task_list(...)")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        if filter is not None:
            query_params["filter"] = _format_filter_item(filter)
        return IterableTransferResponse(
            self.get("task_list", query_params=query_params)
        )

    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def task_event_list(
        self,
        task_id: UUIDLike,
        *,
        limit: int | None = None,
        offset: int | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        r"""
        List events (for example, faults and errors) for a given Task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch 10 events and print some basic info:

                .. code-block:: python

                    tc = TransferClient(...)
                    task_id = ...
                    for event in tc.task_event_list(task_id, limit=10):
                        print(f"Event on Task({task_id}) at {event['time']}:\n{event['description']}")

            .. tab-item:: Paginated Usage

                .. paginatedusage:: task_event_list

            .. tab-item:: API Info

                ``GET /task/<task_id>/event_list``

                .. extdoclink:: Get Event List
                    :ref: transfer/task/#get_event_list
        """  # noqa: E501
        log.info(f"TransferClient.task_event_list({task_id}, ...)")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        return IterableTransferResponse(
            self.get(f"task/{task_id}/event_list", query_params=query_params)
        )

    def get_task(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /task/<task_id>``

                .. extdoclink:: Get task by ID
                    :ref: transfer/task/#get_task_by_id
        """
        log.info(f"TransferClient.get_task({task_id}, ...)")
        return self.get(f"task/{task_id}", query_params=query_params)

    def update_task(
        self,
        task_id: UUIDLike,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Modify a task. Only tasks which are still running can be modified, and only the
        ``label`` and ``deadline`` fields can be updated.

        :param task_id: The ID of the task to modify
        :type task_id: str or UUID
        :param data: A partial task document with fields to update
        :type data: dict
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /task/<task_id>``

                .. extdoclink:: Update task by ID
                    :ref: transfer/task/#update_task_by_id
        """
        log.info(f"TransferClient.update_task({task_id}, ...)")
        return self.put(f"task/{task_id}", data=data, query_params=query_params)

    def cancel_task(self, task_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        Cancel a task which is still running.

        :param task_id: The ID of the task to cancel
        :type task_id: str or UUID

        .. tab-set::

            .. tab-item:: API Info

                ``POST /task/<task_id>/cancel``

                .. extdoclink:: Cancel task by ID
                    :ref: transfer/task/#cancel_task_by_id
        """
        log.info(f"TransferClient.cancel_task({task_id})")
        return self.post(f"task/{task_id}/cancel")

    def task_wait(
        self, task_id: UUIDLike, *, timeout: int = 10, polling_interval: int = 10
    ) -> bool:
        r"""
        Wait until a Task is complete or fails, with a time limit. If the task
        is "ACTIVE" after time runs out, returns ``False``. Otherwise returns
        ``True``.

        :param task_id: ID of the Task to wait on for completion
        :type task_id: str or UUID
        :param timeout: Number of seconds to wait in total. Minimum 1. [Default: ``10``]
        :type timeout: int, optional
        :param polling_interval: Number of seconds between queries to Globus about the
            Task status. Minimum 1. [Default: ``10``]
        :type polling_interval: int, optional

        .. tab-set::

            .. tab-item:: Example Usage

                If you want to wait for a task to terminate, but want to warn every
                minute that it doesn't terminate, you could:

                .. code-block:: python

                    tc = TransferClient(...)
                    while not tc.task_wait(task_id, timeout=60):
                        print(f"Another minute went by without {task_id} terminating")

                Or perhaps you want to check on a task every minute for 10 minutes, and
                give up if it doesn't complete in that time:

                .. code-block:: python

                    tc = TransferClient(...)
                    done = tc.task_wait(task_id, timeout=600, polling_interval=60)
                    if not done:
                        print(f"{task_id} didn't successfully terminate!")
                    else:
                        print(f"{task_id} completed")

                You could print dots while you wait for a task by only waiting one
                second at a time:

                .. code-block:: python

                    tc = TransferClient(...)
                    while not tc.task_wait(task_id, timeout=1, polling_interval=1):
                        print(".", end="")
                    print(f"\n{task_id} completed!")
        """  # noqa: E501
        log.info(
            "TransferClient.task_wait(%s, %s, %s)", task_id, timeout, polling_interval
        )

        # check valid args
        if timeout < 1:
            log.error(f"task_wait() timeout={timeout} is less than minimum of 1s")
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait timeout has a minimum of 1"
            )
        if polling_interval < 1:
            log.error(
                "task_wait() polling_interval={} is less than minimum of 1s".format(
                    polling_interval
                )
            )
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait polling_interval has a minimum of 1"
            )

        # ensure that we always wait at least one interval, even if the timeout
        # is shorter than the polling interval, by reducing the interval to the
        # timeout if it is larger
        polling_interval = min(timeout, polling_interval)

        # helper for readability
        def timed_out(waited_time: int) -> bool:
            return waited_time > timeout

        waited_time = 0
        # doing this as a while-True loop actually makes it simpler than doing
        # while not timed_out(waited_time) because of the end condition
        while True:
            # get task, check if status != ACTIVE
            task = self.get_task(task_id)
            status = task["status"]
            if status != "ACTIVE":
                log.debug(
                    "task_wait(task_id={}) terminated with status={}".format(
                        task_id, status
                    )
                )
                return True

            # make sure to check if we timed out before sleeping again, so we
            # don't sleep an extra polling_interval
            waited_time += polling_interval
            if timed_out(waited_time):
                log.debug(f"task_wait(task_id={task_id}) timed out")
                return False

            log.debug(f"task_wait(task_id={task_id}) waiting {polling_interval}s")
            time.sleep(polling_interval)
        # unreachable -- end of task_wait

    def task_pause_info(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get info about why a task is paused or about to be paused.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /task/<task_id>/pause_info``

                .. extdoclink:: Get task pause info
                    :ref: transfer/task/#get_task_pause_info
        """
        log.info(f"TransferClient.task_pause_info({task_id}, ...)")
        return self.get(f"task/{task_id}/pause_info", query_params=query_params)

    @paging.has_paginator(
        paging.NullableMarkerPaginator, items_key="DATA", marker_key="next_marker"
    )
    def task_successful_transfers(
        self,
        task_id: UUIDLike,
        *,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get the successful file transfers for a completed Task.

        .. note::

            Only files that were actually transferred are included. This does
            not include directories, files that were checked but skipped as
            part of a sync transfer, or files which were skipped due to
            skip_source_errors being set on the task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param marker: A marker for pagination
        :type marker: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch all transferred files for a task and print some basic info:

                .. code-block:: python

                    tc = TransferClient(...)
                    task_id = ...
                    for info in tc.task_successful_transfers(task_id):
                        print(f"{info['source_path']} -> {info['destination_path']}")

            .. tab-item:: Paginated Usage

                .. paginatedusage:: task_successful_transfers

            .. tab-item:: API Info

                ``GET /task/<task_id>/successful_transfers``

                .. extdoclink:: Get Task Successful Transfers
                    :ref: transfer/task/#get_task_successful_transfers
        """  # noqa: E501
        log.info(f"TransferClient.task_successful_transfers({task_id}, ...)")
        if query_params is None:
            query_params = {}
        if marker is not None:
            query_params["marker"] = marker
        return IterableTransferResponse(
            self.get(f"task/{task_id}/successful_transfers", query_params=query_params)
        )

    @paging.has_paginator(
        paging.NullableMarkerPaginator, items_key="DATA", marker_key="next_marker"
    )
    def task_skipped_errors(
        self,
        task_id: UUIDLike,
        *,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get path and error information for all paths that were skipped due
        to skip_source_errors being set on a completed transfer Task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param marker: A marker for pagination
        :type marker: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch all skipped errors for a task and print some basic info:

                .. code-block:: python

                    tc = TransferClient(...)
                    task_id = ...
                    for info in tc.task_skipped_errors(task_id):
                        print(f"{info['error_code']} -> {info['source_path']}")

            .. tab-item:: Paginated Usage

                .. paginatedusage:: task_skipped_errors

            .. tab-item:: API Info

                ``GET /task/<task_id>/skipped_errors``

                .. extdoclink:: Get Task Skipped Errors
                    :ref: transfer/task/#get_task_skipped_errors
        """  # noqa: E501
        log.info("TransferClient.task_skipped_errors(%s, ...)", task_id)
        if query_params is None:
            query_params = {}
        if marker is not None:
            query_params["marker"] = marker
        return IterableTransferResponse(
            self.get(f"task/{task_id}/skipped_errors", query_params=query_params)
        )

    #
    # advanced endpoint management (requires endpoint manager role)
    #

    def endpoint_manager_monitored_endpoints(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> IterableTransferResponse:
        """
        Get endpoints the current user is a monitor or manager on.

        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET endpoint_manager/monitored_endpoints``

                .. extdoclink:: Get monitored endpoints
                    :ref: transfer/advanced_endpoint_management/#get_monitored_endpoints
        """
        log.info(f"TransferClient.endpoint_manager_monitored_endpoints({query_params})")
        return IterableTransferResponse(
            self.get("endpoint_manager/monitored_endpoints", query_params=query_params)
        )

    def endpoint_manager_hosted_endpoint_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get shared endpoints hosted on the given endpoint.

        :param endpoint_id: The ID of the host endpoint
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/endpoint/<endpoint_id>/hosted_endpoint_list``

                .. extdoclink:: Get hosted endpoint list
                    :ref: transfer/advanced_endpoint_management/#get_hosted_endpoint_list
        """  # noqa: E501
        log.info(f"TransferClient.endpoint_manager_hosted_endpoint_list({endpoint_id})")
        return IterableTransferResponse(
            self.get(
                f"endpoint_manager/endpoint/{endpoint_id}/hosted_endpoint_list",
                query_params=query_params,
            )
        )

    def endpoint_manager_get_endpoint(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get endpoint details as an admin.

        :param endpoint_id: The ID of the endpoint
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/endpoint/<endpoint_id>``

                .. extdoclink:: Get endpoint as admin
                    :ref: transfer/advanced_endpoint_management/#mc_get_endpoint
        """
        log.info(f"TransferClient.endpoint_manager_get_endpoint({endpoint_id})")
        return self.get(
            f"endpoint_manager/endpoint/{endpoint_id}", query_params=query_params
        )

    def endpoint_manager_acl_list(
        self,
        endpoint_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get a list of access control rules on specified endpoint as an admin.

        :param endpoint_id: The ID of the endpoint
        :type endpoint_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET endpoint_manager/endpoint/<endpoint_id>/access_list``

                .. extdoclink:: Get endpoint access list as admin
                    :ref: transfer/advanced_endpoint_management/#get_endpoint_access_list_as_admin
        """  # noqa: E501
        log.info(
            f"TransferClient.endpoint_manager_endpoint_acl_list({endpoint_id}, ...)"
        )
        return IterableTransferResponse(
            self.get(
                f"endpoint_manager/endpoint/{endpoint_id}/access_list",
                query_params=query_params,
            )
        )

    #
    # endpoint manager task methods
    #

    @paging.has_paginator(paging.LastKeyPaginator, items_key="DATA")
    def endpoint_manager_task_list(
        self,
        *,
        filter_status: None | str | t.Iterable[str] = None,
        filter_task_id: None | UUIDLike | t.Iterable[UUIDLike] = None,
        filter_owner_id: UUIDLike | None = None,
        filter_endpoint: UUIDLike | None = None,
        filter_is_paused: bool | None = None,
        filter_completion_time: (None | str | tuple[DateLike, DateLike]) = None,
        filter_min_faults: int | None = None,
        filter_local_user: str | None = None,
        last_key: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        r"""
        Get a list of tasks visible via ``activity_monitor`` role, as opposed
        to tasks owned by the current user.

        For any query that doesn't specify a ``filter_status`` that is a subset of
        ``("ACTIVE", "INACTIVE")``, at least one of ``filter_task_id`` or
        ``filter_endpoint`` is required.

        :param filter_status: Return only tasks with any of the specified statuses
            Note that in-progress tasks will have status ``"ACTIVE"`` or ``"INACTIVE"``,
            and completed tasks will have status ``"SUCCEEDED"`` or ``"FAILED"``.
        :type filter_status: str or iterable of str, optional
        :param filter_task_id: Return only tasks with any of the specified ids. If any
            of the specified tasks do not involve an endpoint the user has an
            appropriate role for, a ``PermissionDenied`` error will be returned. This
            filter can't be combined with any other filter.  If another filter is
            passed, a ``BadRequest`` will be returned. (limit: 50 task IDs)
        :type filter_task_id: str, UUID, or iterable of str or UUID, optional
        :param filter_owner_id: A Globus Auth identity id. Limit results to tasks
            submitted by the specified identity, or linked to the specified identity,
            at submit time.  Returns ``UserNotFound`` if the identity does not exist or
            has never used the Globus Transfer service. If no tasks were submitted by
            this user to an endpoint the current user has an appropriate role on, an
            empty result set will be returned. Unless filtering for running tasks (i.e.
            ``filter_status`` is a subset of ``("ACTIVE", "INACTIVE")``,
            ``filter_endpoint`` is required when using ``filter_owner_id``.
        :type filter_owner_id: str or UUID, optional
        :param filter_endpoint: Single endpoint id. Return only tasks with a matching
            source or destination endpoint or matching source or destination host
            endpoint.
        :type filter_endpoint: str or UUID, optional
        :param filter_is_paused: Return only tasks with the specified ``is_paused``
            value. Requires that ``filter_status`` is also passed and contains a subset
            of ``"ACTIVE"`` and ``"INACTIVE"``. Completed tasks always have
            ``is_paused`` equal to ``False`` and filtering on their paused state is not
            useful and not supported.  Note that pausing is an async operation, and
            after a pause rule is inserted it will take time before the ``is_paused``
            flag is set on all affected tasks. Tasks paused by id will have the
            ``is_paused`` flag set immediately.
        :type filter_is_paused: bool, optional
        :param filter_completion_time: Start and end date-times separated by a comma, or
            provided as a tuple of strings or datetime objects.  Returns only completed
            tasks with ``completion_time`` in the specified range. Date strings should
            be specified in one of the following ISO 8601 formats:
            ``YYYY-MM-DDTHH:MM:SS``, ``YYYY-MM-DDTHH:MM:SS+/-HH:MM``, or
            ``YYYY-MM-DDTHH:MM:SSZ``. If no timezone is specified, UTC is assumed. A
            space can be used between the date and time instead of ``T``. A blank string
            may be used for either the start or end (but not both) to indicate no limit
            on that side. If the end date is blank, the filter will also include all
            active tasks, since they will complete some time in the future.
        :type filter_completion_time: str, tuple of str, or tuple of datetime, optional
        :param filter_min_faults:  Minimum number of cumulative faults, inclusive.
            Return only tasks with ``faults >= N``, where ``N`` is the filter value.
            Use ``filter_min_faults=1`` to find all tasks with at least one fault.
            Note that many errors are not fatal and the task may still be successful
            even if ``faults >= 1``.
        :type filter_min_faults: int, optional
        :param filter_local_user: A valid username for the target system running the
            endpoint, as a utf8 encoded string. Requires that ``filter_endpoint`` is
            also set. Return only tasks that have successfully fetched the local user
            from the endpoint, and match the values of ``filter_endpoint`` and
            ``filter_local_user`` on the source or on the destination.
        :type filter_local_user: str, optional
        :param last_key: the last key, for paging
        :type last_key: str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch some tasks and print some basic info:

                .. code-block:: python

                    tc = TransferClient(...)
                    for task in tc.endpoint_manager_task_list(filter_status="ACTIVE"):
                        print(
                            f"Task({task['task_id']}): "
                            f"{task['source_endpoint']} -> {task['destination_endpoint']}\n"
                            "  was submitted by\n"
                            f"  {task['owner_string']}"
                        )

            .. tab-item:: Paginated Usage

                .. paginatedusage:: endpoint_manager_task_list

                For example, fetch and print all active tasks visible via
                ``activity_monitor`` permissions:

                .. code-block:: python

                    tc = TransferClient(...)
                    for page in tc.paginated.endpoint_manager_task_list(filter_status="ACTIVE"):
                        for task in page:
                            print(
                                f"Task({task['task_id']}): "
                                f"{task['source_endpoint']} -> {task['destination_endpoint']}\n"
                                "  was submitted by\n"
                                f"  {task['owner_string']}"
                            )

            .. tab-item:: API Info

                ``GET endpoint_manager/task_list``

                .. extdoclink:: Advanced Endpoint Management: Get tasks
                    :ref: transfer/advanced_endpoint_management/#get_tasks
        """  # noqa: E501
        log.info("TransferClient.endpoint_manager_task_list(...)")
        if query_params is None:
            query_params = {}
        if filter_status is not None:
            if isinstance(filter_status, str):
                query_params["filter_status"] = filter_status
            else:
                query_params["filter_status"] = ",".join(filter_status)
        if filter_task_id is not None:
            if isinstance(filter_task_id, (uuid.UUID, str)):
                query_params["filter_task_id"] = str(filter_task_id)
            else:
                query_params["filter_task_id"] = ",".join(
                    [str(tid) for tid in filter_task_id]
                )
        if filter_owner_id is not None:
            query_params["filter_owner_id"] = str(filter_owner_id)
        if filter_endpoint is not None:
            query_params["filter_endpoint"] = str(filter_endpoint)
        if filter_is_paused is not None:
            query_params["filter_is_paused"] = filter_is_paused
        if filter_completion_time is not None:
            if isinstance(filter_completion_time, str):
                query_params["filter_completion_time"] = filter_completion_time
            else:
                start_t, end_t = filter_completion_time
                start_t, end_t = _datelike_to_str(start_t), _datelike_to_str(end_t)
                query_params["filter_completion_time"] = f"{start_t},{end_t}"
        if filter_min_faults is not None:
            query_params["filter_min_faults"] = filter_min_faults
        if filter_local_user is not None:
            query_params["filter_local_user"] = filter_local_user
        if last_key is not None:
            query_params["last_key"] = last_key
        return IterableTransferResponse(
            self.get("endpoint_manager/task_list", query_params=query_params)
        )

    def endpoint_manager_get_task(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get task info as an admin. Requires activity monitor effective role on
        the destination endpoint of the task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/task/<task_id>``

                .. extdoclink:: Get task as admin
                    :ref: transfer/advanced_endpoint_management/#get_task
        """
        log.info(f"TransferClient.endpoint_manager_get_task({task_id}, ...)")
        return self.get(f"endpoint_manager/task/{task_id}", query_params=query_params)

    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def endpoint_manager_task_event_list(
        self,
        task_id: UUIDLike,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filter_is_error: bool | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        List events (for example, faults and errors) for a given task as an
        admin. Requires activity monitor effective role on the destination
        endpoint of the task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :param filter_is_error: Return only events that are errors. A value of ``False``
            (returning only non-errors) is not supported. By default all events are
            returned.
        :type filter_is_error: bool, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: endpoint_manager_task_event_list

            .. tab-item:: API Info

                ``GET /task/<task_id>/event_list``

                .. extdoclink:: Get task events as admin
                    :ref: transfer/advanced_endpoint_management/#get_task_events
        """
        log.info(f"TransferClient.endpoint_manager_task_event_list({task_id}, ...)")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        if filter_is_error is not None:
            query_params["filter_is_error"] = 1 if filter_is_error else 0
        return IterableTransferResponse(
            self.get(
                f"endpoint_manager/task/{task_id}/event_list", query_params=query_params
            )
        )

    def endpoint_manager_task_pause_info(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get details about why a task is paused as an admin. Requires activity
        monitor effective role on the destination endpoint of the task.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/task/<task_id>/pause_info``

                .. extdoclink:: Get task pause info as admin
                    :ref: transfer/advanced_endpoint_management/#get_task_pause_info_as_admin
        """  # noqa: E501
        log.info(f"TransferClient.endpoint_manager_task_pause_info({task_id}, ...)")
        return self.get(
            f"endpoint_manager/task/{task_id}/pause_info", query_params=query_params
        )

    @paging.has_paginator(
        paging.NullableMarkerPaginator, items_key="DATA", marker_key="next_marker"
    )
    def endpoint_manager_task_successful_transfers(
        self,
        task_id: UUIDLike,
        *,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        r"""
        Get the successful file transfers for a completed Task as an admin.

        :param task_id: The ID of the task to inspect
        :type task_id: str or UUID
        :param marker: A marker for pagination
        :type marker: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: endpoint_manager_task_successful_transfers

            .. tab-item:: API Info

                ``GET /endpoint_manager/task/<task_id>/successful_transfers``

                .. extdoclink:: Get task successful transfers as admin
                    :ref: transfer/advanced_endpoint_management/\
                            #get_task_successful_transfers_as_admin
        """
        log.info(
            "TransferClient.endpoint_manager_task_successful_transfers(%s, ...)",
            task_id,
        )
        if query_params is None:
            query_params = {}
        if marker is not None:
            query_params["marker"] = marker
        return IterableTransferResponse(
            self.get(
                f"endpoint_manager/task/{task_id}/successful_transfers",
                query_params=query_params,
            )
        )

    @paging.has_paginator(
        paging.NullableMarkerPaginator, items_key="DATA", marker_key="next_marker"
    )
    def endpoint_manager_task_skipped_errors(
        self,
        task_id: UUIDLike,
        *,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        r"""
        Get skipped errors for a completed Task as an admin.

        :param task_id: The ID of the task to inspect
        :type task_id: str
        :param marker: A marker for pagination
        :type marker: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: endpoint_manager_task_skipped_errors

            .. tab-item:: API Info

                ``GET /endpoint_manager/task/<task_id>/skipped_errors``

                .. extdoclink:: Get task skipped errors as admin
                    :ref: transfer/advanced_endpoint_management/\
                            #get_task_skipped_errors_as_admin
        """
        log.info(f"TransferClient.endpoint_manager_task_skipped_errors({task_id}, ...)")
        if query_params is None:
            query_params = {}
        if marker is not None:
            query_params["marker"] = marker
        return IterableTransferResponse(
            self.get(
                f"endpoint_manager/task/{task_id}/skipped_errors",
                query_params=query_params,
            )
        )

    def endpoint_manager_cancel_tasks(
        self,
        task_ids: t.Iterable[UUIDLike],
        message: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Cancel a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        :param task_ids: List of task ids to cancel
        :type task_ids: iterable of str or UUID
        :param message: Message given to all users whose tasks have been canceled
        :type message: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint_manager/admin_cancel``

                .. extdoclink:: Cancel tasks as admin
                    :ref: transfer/advanced_endpoint_management/#admin_cancel
        """
        str_task_ids = [str(i) for i in task_ids]
        log.info(
            f"TransferClient.endpoint_manager_cancel_tasks({str_task_ids}, {message})"
        )
        data = {"message": message, "task_id_list": str_task_ids}
        return self.post(
            "endpoint_manager/admin_cancel", data=data, query_params=query_params
        )

    def endpoint_manager_cancel_status(
        self,
        admin_cancel_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get the status of an an admin cancel (result of
        endpoint_manager_cancel_tasks).

        :param admin_cancel_id: The ID of the the cancel job to inspect
        :type admin_cancel_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/admin_cancel/<admin_cancel_id>``

                .. extdoclink:: Get cancel status by ID
                    :ref: transfer/advanced_endpoint_management/#get_cancel_status_by_id
        """
        log.info(f"TransferClient.endpoint_manager_cancel_status({admin_cancel_id})")
        return self.get(
            f"endpoint_manager/admin_cancel/{admin_cancel_id}",
            query_params=query_params,
        )

    def endpoint_manager_pause_tasks(
        self,
        task_ids: t.Iterable[UUIDLike],
        message: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Pause a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        :param task_ids: List of task ids to pause
        :type task_ids: iterable of str or UUID
        :param message: Message given to all users whose tasks have been paused
        :type message: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint_manager/admin_pause``

                .. extdoclink:: Pause tasks as admin
                    :ref: transfer/advanced_endpoint_management/#pause_tasks_as_admin
        """
        str_task_ids = [str(i) for i in task_ids]
        log.info(
            f"TransferClient.endpoint_manager_pause_tasks({str_task_ids}, {message})"
        )
        data = {"message": message, "task_id_list": str_task_ids}
        return self.post(
            "endpoint_manager/admin_pause", data=data, query_params=query_params
        )

    def endpoint_manager_resume_tasks(
        self,
        task_ids: t.Iterable[UUIDLike],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Resume a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        :param task_ids: List of task ids to resume
        :type task_ids: iterable of str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``POST /endpoint_manager/admin_resume``

                .. extdoclink:: Resume tasks as admin
                    :ref: transfer/advanced_endpoint_management/#resume_tasks_as_admin
        """
        str_task_ids = [str(i) for i in task_ids]
        log.info(f"TransferClient.endpoint_manager_resume_tasks({str_task_ids})")
        data = {"task_id_list": str_task_ids}
        return self.post(
            "endpoint_manager/admin_resume", data=data, query_params=query_params
        )

    #
    # endpoint manager pause rule methods
    #

    def endpoint_manager_pause_rule_list(
        self,
        *,
        filter_endpoint: UUIDLike | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableTransferResponse:
        """
        Get a list of pause rules on endpoints that the current user has the
        activity monitor effective role on.

        :param filter_endpoint: An endpoint ID. Limit results to rules on endpoints
            hosted by this endpoint. Must be activity monitor on this endpoint, not just
            the hosted endpoints.
        :type filter_endpoint: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/pause_rule_list``

                .. extdoclink:: Get pause rules
                    :ref: transfer/advanced_endpoint_management/#get_pause_rules
        """
        log.info("TransferClient.endpoint_manager_pause_rule_list(...)")
        if query_params is None:
            query_params = {}
        if filter_endpoint is not None:
            query_params["filter_endpoint"] = str(filter_endpoint)
        return IterableTransferResponse(
            self.get("endpoint_manager/pause_rule_list", query_params=query_params)
        )

    def endpoint_manager_create_pause_rule(
        self, data: dict[str, t.Any] | None
    ) -> response.GlobusHTTPResponse:
        """
        Create a new pause rule. Requires the activity manager effective role
        on the endpoint defined in the rule.

        :param data: A pause rule document describing the rule to create
        :type data: dict

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    rule_data = {
                        "DATA_TYPE": "pause_rule",
                        "message": "Message to users explaining why tasks are paused",
                        "endpoint_id": "339abc22-aab3-4b45-bb56-8d40535bfd80",
                        "identity_id": None,  # affect all users on endpoint
                        "start_time": None,  # start now
                    }
                    create_result = tc.endpoint_manager_create_pause_rule(ep_data)
                    rule_id = create_result["id"]

            .. tab-item:: API Info

                ``POST /endpoint_manager/pause_rule``

                .. extdoclink:: Create pause rule
                    :ref: transfer/advanced_endpoint_management/#create_pause_rule
        """
        log.info("TransferClient.endpoint_manager_create_pause_rule(...)")
        return self.post("endpoint_manager/pause_rule", data=data)

    def endpoint_manager_get_pause_rule(
        self,
        pause_rule_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.

        :param pause_rule_id: ID of pause rule to get
        :type pause_rule_id: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``GET /endpoint_manager/pause_rule/<pause_rule_id>``

                .. extdoclink:: Get pause rule
                    :ref: transfer/advanced_endpoint_management/#get_pause_rule
        """
        log.info(f"TransferClient.endpoint_manager_get_pause_rule({pause_rule_id})")
        return self.get(
            f"endpoint_manager/pause_rule/{pause_rule_id}", query_params=query_params
        )

    def endpoint_manager_update_pause_rule(
        self,
        pause_rule_id: UUIDLike,
        data: dict[str, t.Any] | None,
    ) -> response.GlobusHTTPResponse:
        """
        Update an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.
        Note that non update-able fields in data will be ignored.

        :param pause_rule_id: The ID of the pause rule to update
        :type pause_rule_id: str
        :param data: A partial pause rule document with fields to update
        :type data: dict

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TransferClient(...)
                    rule_data = {
                        "message": "Update to pause, reads are now allowed.",
                        "pause_ls": False,
                        "pause_task_transfer_read": False,
                    }
                    update_result = tc.endpoint_manager_update_pause_rule(ep_data)

            .. tab-item:: API Info

                ``PUT /endpoint_manager/pause_rule/<pause_rule_id>``

                .. extdoclink:: Update pause rule
                    :ref: transfer/advanced_endpoint_management/#update_pause_rule
        """
        log.info(f"TransferClient.endpoint_manager_update_pause_rule({pause_rule_id})")
        return self.put(f"endpoint_manager/pause_rule/{pause_rule_id}", data=data)

    def endpoint_manager_delete_pause_rule(
        self,
        pause_rule_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete an existing pause rule by ID. Requires the user to see the
        "editable" field of the rule as True. Any tasks affected by this rule
        will no longer be once it is deleted.

        :param pause_rule_id: The ID of the pause rule to delete
        :type pause_rule_id: str
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /endpoint_manager/pause_rule/<pause_rule_id>``

                .. extdoclink:: Delete pause rule
                    :ref: transfer/advanced_endpoint_management/#delete_pause_rule
        """
        log.info(f"TransferClient.endpoint_manager_delete_pause_rule({pause_rule_id})")
        return self.delete(
            f"endpoint_manager/pause_rule/{pause_rule_id}", query_params=query_params
        )
