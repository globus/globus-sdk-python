from __future__ import annotations

import logging
import typing as t

from globus_sdk import client, paging, response, utils
from globus_sdk._types import UUIDLike
from globus_sdk.exc.warnings import warn_deprecated
from globus_sdk.scopes import SearchScopes

from .data import SearchQuery, SearchScrollQuery
from .errors import SearchAPIError

log = logging.getLogger(__name__)


class SearchClient(client.BaseClient):
    r"""
    Client for the Globus Search API

    This class provides helper methods for most common resources in the
    API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base client that can be used to access any API resource.

    :param authorizer: An authorizer instance used for all calls to
                       Globus Search
    :type authorizer: :class:`GlobusAuthorizer \
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`

    **Methods**

    .. automethodlist:: globus_sdk.SearchClient
    """
    error_class = SearchAPIError
    service_name = "search"
    scopes = SearchScopes

    #
    # Index Management
    #

    @utils.doc_api_method("Get Index Metadata", "search/reference/index_show/")
    def get_index(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>``

        Get descriptive data about a Search index, including its title and description
        and how much data it contains.

        :param index_id: the ID of the index
        :type index_id: str or UUID
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> index = sc.get_index(index_id)
        >>> assert index['id'] == index_id
        >>> print(index["display_name"],
        >>>       "(" + index_id + "):",
        >>>       index["description"])
        """
        log.info(f"SearchClient.get_index({index_id})")
        return self.get(f"/v1/index/{index_id}", query_params=query_params)

    #
    # Search queries
    #

    @paging.has_paginator(
        paging.HasNextPaginator,
        items_key="gmeta",
        get_page_size=lambda x: x["count"],
        max_total_results=10000,
        page_size=100,
    )
    def search(
        self,
        index_id: UUIDLike,
        q: str,
        *,
        offset: int = 0,
        limit: int = 10,
        advanced: bool = False,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Execute a simple Search Query, described by the query string ``q``.

        :param index_id: the ID of the index
        :type index_id: str or UUID
        :param q: the query string
        :type q: str
        :param offset: an offset for pagination
        :type offset: int
        :param limit: the size of a page of results
        :type limit: int
        :param advanced: enable 'advanced' query mode, which has sophisticated syntax
            but may result in BadRequest errors when used if the query is invalid
        :type advanced: bool
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block::

                    sc = globus_sdk.SearchClient(...)
                    result = sc.search(index_id, "query string")
                    advanced_result = sc.search(index_id, 'author: "Ada Lovelace"', advanced=True)

            .. tab-item:: Paginated Usage

                .. paginatedusage:: search

            .. tab-item:: API Info

                ``GET /v1/index/<index_id>/search``

                .. extdoclink:: GET Search Query
                    :ref: search/reference/get_query/

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.search
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        query_params.update(
            {
                "q": q,
                "offset": offset,
                "limit": limit,
                "advanced": advanced,
            }
        )

        log.info(f"SearchClient.search({index_id}, ...)")
        return self.get(f"/v1/index/{index_id}/search", query_params=query_params)

    @paging.has_paginator(
        paging.HasNextPaginator,
        items_key="gmeta",
        get_page_size=lambda x: x["count"],
        max_total_results=10000,
        page_size=100,
    )
    def post_search(
        self,
        index_id: UUIDLike,
        data: dict[str, t.Any] | SearchQuery,
        *,
        offset: int | None = None,
        limit: int | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Execute a complex Search Query, using a query document to express filters,
        facets, sorting, field boostring, and other behaviors.

        :param index_id: The index on which to search
        :type index_id: str or UUID
        :param data: A Search Query document containing the query and any other fields
        :type data: dict or SearchQuery
        :param offset: offset used in paging (overwrites any offset in ``data``)
        :type offset: int, optional
        :param limit: limit the number of results (overwrites any limit in ``data``)
        :type limit: int, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block::

                    sc = globus_sdk.SearchClient(...)
                    query_data = {
                        "q": "user query",
                        "filters": [
                            {
                                "type": "range",
                                "field_name": "path.to.date",
                                "values": [{"from": "*", "to": "2014-11-07"}],
                            }
                        ],
                        "facets": [
                            {
                                "name": "Publication Date",
                                "field_name": "path.to.date",
                                "type": "date_histogram",
                                "date_interval": "year",
                            }
                        ],
                        "sort": [{"field_name": "path.to.date", "order": "asc"}],
                    }
                    search_result = sc.post_search(index_id, query_data)

            .. tab-item:: Paginated Usage

                .. paginatedusage:: post_search

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/search``

                .. extdoclink:: POST Search Query
                    :ref: search/reference/post_query/
        """
        log.info(f"SearchClient.post_search({index_id}, ...)")
        add_kwargs = {}
        if offset is not None:
            add_kwargs["offset"] = offset
        if limit is not None:
            add_kwargs["limit"] = limit
        if add_kwargs:
            data = {**data, **add_kwargs}
        return self.post(f"v1/index/{index_id}/search", data=data)

    @paging.has_paginator(paging.MarkerPaginator, items_key="gmeta")
    def scroll(
        self,
        index_id: UUIDLike,
        data: dict[str, t.Any] | SearchScrollQuery,
        *,
        marker: str | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Scroll all data in a Search index. The paginated version of this API should
        typically be preferred, as it is the intended mode of usage.

        Note that if data is written or deleted during scrolling, it is possible for
        scrolling to not include results or show other unexpected behaviors.

        :param index_id: The index on which to search
        :type index_id: str or UUID
        :param data: A Search Scroll Query document
        :type data: dict or SearchScrollQuery
        :param marker: marker used in paging (overwrites any marker in ``data``)
        :type marker: str, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block::

                    sc = globus_sdk.SearchClient(...)
                    scroll_result = sc.scroll(index_id, {"q": "*"})

            .. tab-item:: Paginated Usage

                .. paginatedusage:: scroll

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/scroll``

                .. extdoclink:: Scroll Query
                    :ref: search/reference/scroll_query/
        """
        log.info(f"SearchClient.scroll({index_id}, ...)")
        add_kwargs = {}
        if marker is not None:
            add_kwargs["marker"] = marker
        if add_kwargs:
            data = {**data, **add_kwargs}
        return self.post(f"v1/index/{index_id}/scroll", data=data)

    #
    # Bulk data indexing
    #

    @utils.doc_api_method("Ingest", "search/reference/ingest")
    def ingest(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/ingest``

        Write data to a Search index as an asynchronous task.
        The data can be provided as a single document or list of documents, but only one
        ``task_id`` value will be included in the response.

        :param index_id: The index into which to write data
        :type index_id: str or UUID
        :param data: an ingest document
        :type data: dict

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> ingest_data = {
        >>>   "ingest_type": "GMetaEntry",
        >>>   "ingest_data": {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>       "foo/bar": "some val"
        >>>     }
        >>>   }
        >>> }
        >>> sc.ingest(index_id, ingest_data)

        or with multiple entries at once via a GMetaList:

        >>> sc = globus_sdk.SearchClient(...)
        >>> ingest_data = {
        >>>   "ingest_type": "GMetaList",
        >>>   "ingest_data": {
        >>>     "gmeta": [
        >>>       {
        >>>         "subject": "https://example.com/foo/bar",
        >>>         "visible_to": ["public"],
        >>>         "content": {
        >>>           "foo/bar": "some val"
        >>>         }
        >>>       },
        >>>       {
        >>>         "subject": "https://example.com/foo/bar",
        >>>         "id": "otherentry",
        >>>         "visible_to": ["public"],
        >>>         "content": {
        >>>           "foo/bar": "some otherval"
        >>>         }
        >>>       }
        >>>     ]
        >>>   }
        >>> }
        >>> sc.ingest(index_id, ingest_data)
        """
        log.info(f"SearchClient.ingest({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/ingest", data=data)

    #
    # Bulk delete
    #

    @utils.doc_api_method("Delete By Query", "search/reference/delete_by_query")
    def delete_by_query(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/delete_by_query``

        Delete data in a Search index as an asynchronous task, deleting all documents
        which match a given query.
        The query uses a restricted subset of the syntax available for complex queries,
        as it is not meaningful to boost, sort, or otherwise rank data in this case.

        A ``task_id`` value will be included in the response.

        :param index_id: The index in which to delete data
        :type index_id: str or UUID
        :param data: a query document for documents to delete
        :type data: dict

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> query_data = {
        >>>   "q": "user query",
        >>>   "filters": [
        >>>     {
        >>>       "type": "range",
        >>>       "field_name": "path.to.date",
        >>>       "values": [
        >>>         {"from": "*",
        >>>          "to": "2014-11-07"}
        >>>       ]
        >>>     }
        >>>   ]
        >>> }
        >>> sc.delete_by_query(index_id, query_data)
        """
        log.info(f"SearchClient.delete_by_query({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/delete_by_query", data=data)

    #
    # Subject Operations
    #

    @utils.doc_api_method("Get Subject", "search/reference/get_subject")
    def get_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/subject``

        Fetch exactly one Subject document from Search, containing one or more Entries.

        :param index_id: the index containing this Subject
        :type index_id: str or UUID
        :param subject: the subject string to fetch
        :type subject: str
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        Fetch the data for subject ``http://example.com/abc`` from index
        ``index_id``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> subject_data = sc.get_subject(index_id, 'http://example.com/abc')
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        log.info(f"SearchClient.get_subject({index_id}, {subject}, ...)")
        return self.get(f"/v1/index/{index_id}/subject", query_params=query_params)

    @utils.doc_api_method("Delete Subject", "search/reference/delete_subject")
    def delete_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /v1/index/<index_id>/subject``

        Delete exactly one Subject document from Search, containing one or more Entries,
        as an asynchronous task.

        A ``task_id`` value will be included in the response.

        :param index_id: the index in which data will be deleted
        :type index_id: str or UUID
        :param subject: the subject string for the Subject document to delete
        :type subject: str
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        Delete all data for subject ``http://example.com/abc`` from index
        ``index_id``, even data which is not visible to the current user:

        >>> sc = globus_sdk.SearchClient(...)
        >>> subject_data = sc.delete_subject(index_id, 'http://example.com/abc')
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject

        log.info(f"SearchClient.delete_subject({index_id}, {subject}, ...)")
        return self.delete(f"/v1/index/{index_id}/subject", query_params=query_params)

    #
    # Entry Operations
    #

    @utils.doc_api_method("Get Entry", "search/reference/get_entry")
    def get_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/entry``

        Fetch exactly one Entry document from Search, identified by the combination of
        ``subject`` string and ``entry_id``, which defaults to ``null``.

        :param index_id: the index containing this Entry
        :type index_id: str or UUID
        :param subject: the subject string for the Subject document containing this
            Entry
        :type subject: str
        :param entry_id: the entry_id for this Entry, which defaults to ``null``
        :type entry_id: str, optional
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        Lookup the entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> entry_data = sc.get_entry(index_id, 'http://example.com/foo/bar')

        Lookup the entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of ``foo/bar``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> entry_data = sc.get_entry(index_id, 'http://example.com/foo/bar',
        >>>                           entry_id='foo/bar')
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id

        log.info(
            "SearchClient.get_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.get(f"/v1/index/{index_id}/entry", query_params=query_params)

    @utils.doc_api_method("Create Entry", "search/reference/create_or_update_entry")
    def create_entry(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        This API method is in effect an alias of ingest and is deprecated.
        Users are recommended to use :meth:`~.ingest` instead.

        ``POST /v1/index/<index_id>/entry``

        Create or update one Entry document in Search.

        The API does not enforce that the document does not exist, and will overwrite
        any existing data.

        :param index_id: the index containing this Entry
        :type index_id: str or UUID
        :param data: the entry document to write
        :type data: dict

        **Examples**

        Create an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.create_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })

        Create an entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of ``foo/bar``:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.create_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "id": "foo/bar",
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })
        """
        warn_deprecated(
            "SearchClient.create_entry is deprecated. "
            "Users should prefer using `SearchClient.ingest`"
        )
        log.info(f"SearchClient.create_entry({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/entry", data=data)

    @utils.doc_api_method("Update Entry", "search/reference/create_or_update_entry")
    def update_entry(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        This API method is in effect an alias of ingest and is deprecated.
        Users are recommended to use :meth:`~.ingest` instead.

        ``PUT /v1/index/<index_id>/entry``

        Create or update one Entry document in Search.

        This does not do a partial update, but replaces the existing document.

        :param index_id: the index containing this Entry
        :type index_id: str or UUID
        :param data: the entry document to write
        :type data: dict

        **Examples**

        Update an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.update_entry(index_id, {
        >>>     "subject": "https://example.com/foo/bar",
        >>>     "visible_to": ["public"],
        >>>     "content": {
        >>>         "foo/bar": "some val"
        >>>     }
        >>> })
        """
        warn_deprecated(
            "SearchClient.update_entry is deprecated. "
            "Users should prefer using `SearchClient.ingest`"
        )
        log.info(f"SearchClient.update_entry({index_id}, ...)")
        return self.put(f"/v1/index/{index_id}/entry", data=data)

    @utils.doc_api_method("Delete Entry", "search/reference/delete_entry")
    def delete_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE  /v1/index/<index_id>/entry``

        Delete exactly one Entry document in Search as an asynchronous task.

        A ``task_id`` value will be included in the response.

        :param index_id: the index in which data will be deleted
        :type index_id: str or UUID
        :param subject: the subject string for the Subject of the document to delete
        :type subject: str
        :param entry_id: the ID string for the Entry to delete
        :type entry_id: str
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        Delete an entry with a subject of ``https://example.com/foo/bar`` and
        a null entry_id:

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.delete_entry(index_id, "https://example.com/foo/bar")

        Delete an entry with a subject of ``https://example.com/foo/bar`` and
        an entry_id of "foo/bar":

        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.delete_entry(index_id, "https://example.com/foo/bar",
        >>>                 entry_id="foo/bar")
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id
        log.info(
            "SearchClient.delete_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.delete(f"/v1/index/{index_id}/entry", query_params=query_params)

    #
    # Task Management
    #

    @utils.doc_api_method("Get Task", "search/reference/get_task")
    def get_task(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/task/<task_id>``

        Fetch a Task document by ID, getting task details and status.

        :param task_id: the task ID from the original task submission
        :type task_id: str or UUID
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> task = sc.get_task(task_id)
        >>> assert task['index_id'] == known_index_id
        >>> print(task["task_id"] + " | " + task['state'])
        """
        log.info(f"SearchClient.get_task({task_id})")
        return self.get(f"/v1/task/{task_id}", query_params=query_params)

    @utils.doc_api_method("Task List", "search/reference/task_list")
    def get_task_list(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/task_list/<index_id>``

        Fetch a list of recent Task documents for an index, getting task details and
        status.

        :param index_id: the index to query
        :type index_id: str or UUID
        :param query_params: additional parameters to pass as query params
        :type query_params: dict, optional

        **Examples**

        >>> sc = globus_sdk.SearchClient(...)
        >>> task_list = sc.get_task_list(index_id)
        >>> for task in task_list['tasks']:
        >>>     print(task["task_id"] + " | " + task['state'])
        """
        log.info(f"SearchClient.get_task_list({index_id})")
        return self.get(f"/v1/task_list/{index_id}", query_params=query_params)

    #
    # Role Management
    #

    @utils.doc_api_method("Create Role", "search/reference/role_create/")
    def create_role(
        self,
        index_id: UUIDLike,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /v1/index/<index_id>/role``

        Create a new role on an index. You must already have the ``owner`` or
        ``admin`` role on an index to create additional roles.

        Roles are specified as a role name (one of ``"owner"``, ``"admin"``, or
        ``"writer"``) and a `Principal URN
        <https://docs.globus.org/api/search/overview/#principal_urns>`_.

        :param index_id: The index on which to create the role
        :type index_id: uuid or str
        :param data: The partial role document to use for creation
        :type data: dict
        :param query_params: Any additional query params to pass
        :type query_params: dict, optional

        **Examples**

        >>> identity_id = "46bd0f56-e24f-11e5-a510-131bef46955c"
        >>> sc = globus_sdk.SearchClient(...)
        >>> sc.create_role(
        >>>     index_id,
        >>>     {
        >>>         "role_name": "writer",
        >>>         "principal": f"urn:globus:auth:identity:{identity_id}"
        >>>     }
        >>> )
        """
        log.info("SearchClient.create_role(%s, ...)", index_id)
        return self.post(
            f"/v1/index/{index_id}/role", data=data, query_params=query_params
        )

    @utils.doc_api_method("Get Role List", "search/reference/role_list/")
    def get_role_list(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /v1/index/<index_id>/role_list``

        List all roles on an index. You must have the ``owner`` or ``admin``
        role on an index to list roles.

        :param index_id: The index on which to list roles
        :type index_id: uuid or str
        :param query_params: Any additional query params to pass
        :type query_params: dict, optional
        """
        log.info("SearchClient.get_role_list(%s)", index_id)
        return self.get(f"/v1/index/{index_id}/role_list", query_params=query_params)

    @utils.doc_api_method("Role Delete", "search/reference/role_delete/")
    def delete_role(
        self,
        index_id: UUIDLike,
        role_id: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /v1/index/<index_id>/role/<role_id>``

        Delete a role from an index. You must have the ``owner`` or ``admin``
        role on an index to delete roles. You cannot remove the last ``owner`` from an
        index.

        :param index_id: The index from which to delete a role
        :type index_id: uuid or str
        :param role_id: The role to delete
        :type role_id: str
        :param query_params: Any additional query params to pass
        :type query_params: dict, optional
        """
        log.info("SearchClient.delete_role(%s, %s)", index_id, role_id)
        return self.delete(
            f"/v1/index/{index_id}/role/{role_id}", query_params=query_params
        )
