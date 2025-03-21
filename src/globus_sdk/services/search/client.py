from __future__ import annotations

import logging
import typing as t

from globus_sdk import client, paging, response, utils
from globus_sdk._types import UUIDLike
from globus_sdk.exc.warnings import warn_deprecated
from globus_sdk.scopes import Scope, SearchScopes

from .data import SearchQuery, SearchScrollQuery
from .errors import SearchAPIError
from .response import IndexListResponse

log = logging.getLogger(__name__)


class SearchClient(client.BaseClient):
    r"""
    Client for the Globus Search API

    .. sdk-sphinx-copy-params:: BaseClient

    This class provides helper methods for most common resources in the
    API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base client that can be used to access any API resource.

    .. automethodlist:: globus_sdk.SearchClient
    """

    error_class = SearchAPIError
    service_name = "search"
    scopes = SearchScopes

    #
    # Index Management
    #

    @property
    def default_scope_requirements(self) -> list[Scope]:
        return [Scope(SearchScopes.search)]

    def create_index(
        self, display_name: str, description: str
    ) -> response.GlobusHTTPResponse:
        """
        Create a new index.

        :param display_name: the name of the index
        :param description: a description of the index

        New indices default to trial status. For subscribers with a subscription ID,
        indices can be converted to non-trial by sending a request to support@globus.org

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    r = sc.create_index(
                        "History and Witchcraft",
                        "Searchable information about history and witchcraft",
                    )
                    print(f"index ID: {r['id']}")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.create_index

            .. tab-item:: API Info

                ``POST /v1/index``

                .. extdoclink:: Index Create
                    :ref: search/reference/index_create/
        """
        log.debug(f"SearchClient.create_index({display_name!r}, ...)")
        return self.post(
            "/v1/index", data={"display_name": display_name, "description": description}
        )

    def delete_index(self, index_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        Mark an index for deletion.

        Globus Search does not immediately delete indices. Instead, this API sets the
        index status to ``"delete-pending"``.
        Search will move pending tasks on the index to the ``CANCELLED`` state and will
        eventually delete the index.

        If the index is a trial index, it will be deleted a few minutes after being
        marked for deletion.
        If the index is non-trial, it will be kept for 30 days and will be eligible for
        use with the ``reopen`` API (see :meth:`~.reopen_index`) during that time.

        :param index_id: the ID of the index

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.delete_index(index_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.delete_index

            .. tab-item:: API Info

                ``DELETE /v1/index/<index_id>``

                .. extdoclink:: Index Delete
                    :ref: search/reference/index_delete/
        """
        log.debug(f"SearchClient.delete_index({index_id!r}, ...)")
        return self.delete(f"/v1/index/{index_id}")

    def reopen_index(self, index_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        Reopen an index that has been marked for deletion, cancelling the deletion.

        :param index_id: the ID of the index

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.reopen_index(index_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.reopen_index

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/reopen``

                .. extdoclink:: Index Reopen
                    :ref: search/reference/index_reopen/
        """
        log.debug(f"SearchClient.reopen_index({index_id!r}, ...)")
        return self.post(f"/v1/index/{index_id}/reopen")

    def get_index(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get descriptive data about a Search index, including its title and description
        and how much data it contains.

        :param index_id: the ID of the index
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    index = sc.get_index(index_id)
                    assert index["id"] == index_id
                    print(index["display_name"], "(" + index_id + "):", index["description"])

            .. tab-item:: API Info

                ``GET /v1/index/<index_id>``

                .. extdoclink:: Index Show
                    :ref: search/reference/index_show/
        """  # noqa: E501
        log.debug(f"SearchClient.get_index({index_id})")
        return self.get(f"/v1/index/{index_id}", query_params=query_params)

    def index_list(
        self,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.IterableResponse:
        """
        Get a list of indices on which the caller has permissions.

        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    for index_doc in sc.index_list():
                        print(index_doc["display_name"], f"({index_doc['id']}):")
                        print("  permissions:", ", ".join(index_doc["permissions"]))

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.index_list

            .. tab-item:: API Info

                ``GET /v1/index_list``

                .. extdoclink:: Index List
                    :ref: search/reference/index_list/
        """  # noqa: E501
        log.debug("SearchClient.index_list()")
        return IndexListResponse(self.get("/v1/index_list", query_params=query_params))

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
        :param q: the query string
        :param offset: an offset for pagination
        :param limit: the size of a page of results
        :param advanced: enable 'advanced' query mode, which has sophisticated syntax
            but may result in BadRequest errors when used if the query is invalid
        :param query_params: additional parameters to pass as query params

        For details on query syntax, including the ``advanced`` query behavior, see
        the :extdoclink:`Search Query Syntax <search/query#query_syntax>` documentation.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

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

        log.debug(f"SearchClient.search({index_id}, ...)")
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
        :param data: A Search Query document containing the query and any other fields
        :param offset: offset used in paging (overwrites any offset in ``data``)
        :param limit: limit the number of results (overwrites any limit in ``data``)

        For details on query syntax, including the ``advanced`` query behavior, see
        the :extdoclink:`Search Query Syntax <search/query#query_syntax>` documentation.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

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
        log.debug(f"SearchClient.post_search({index_id}, ...)")
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
        :param data: A Search Scroll Query document
        :param marker: marker used in paging (overwrites any marker in ``data``)

        For details on query syntax, including the ``advanced`` query behavior, see
        the :extdoclink:`Search Query Syntax <search/query#query_syntax>` documentation.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    scroll_result = sc.scroll(index_id, {"q": "*"})

            .. tab-item:: Paginated Usage

                .. paginatedusage:: scroll

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/scroll``

                .. extdoclink:: Scroll Query
                    :ref: search/reference/scroll_query/
        """
        log.debug(f"SearchClient.scroll({index_id}, ...)")
        add_kwargs = {}
        if marker is not None:
            add_kwargs["marker"] = marker
        if add_kwargs:
            data = {**data, **add_kwargs}
        return self.post(f"v1/index/{index_id}/scroll", data=data)

    #
    # Bulk data indexing
    #

    def ingest(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        Write data to a Search index as an asynchronous task.
        The data can be provided as a single document or list of documents, but only one
        ``task_id`` value will be included in the response.

        :param index_id: The index into which to write data
        :param data: an ingest document

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    ingest_data = {
                        "ingest_type": "GMetaEntry",
                        "ingest_data": {
                            "subject": "https://example.com/foo/bar",
                            "visible_to": ["public"],
                            "content": {"foo/bar": "some val"},
                        },
                    }
                    sc.ingest(index_id, ingest_data)

                or with multiple entries at once via a GMetaList:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    ingest_data = {
                        "ingest_type": "GMetaList",
                        "ingest_data": {
                            "gmeta": [
                                {
                                    "subject": "https://example.com/foo/bar",
                                    "visible_to": ["public"],
                                    "content": {"foo/bar": "some val"},
                                },
                                {
                                    "subject": "https://example.com/foo/bar",
                                    "id": "otherentry",
                                    "visible_to": ["public"],
                                    "content": {"foo/bar": "some otherval"},
                                },
                            ]
                        },
                    }
                    sc.ingest(index_id, ingest_data)

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/ingest``

                .. extdoclink:: Ingest
                    :ref: search/reference/ingest/
        """
        log.debug(f"SearchClient.ingest({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/ingest", data=data)

    #
    # Bulk delete
    #

    def delete_by_query(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        Delete data in a Search index as an asynchronous task, deleting all documents
        which match a given query.
        The query uses a restricted subset of the syntax available for complex queries,
        as it is not meaningful to boost, sort, or otherwise rank data in this case.

        A ``task_id`` value will be included in the response.

        :param index_id: The index in which to delete data
        :param data: a query document for documents to delete

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

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
                    }
                    sc.delete_by_query(index_id, query_data)

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/delete_by_query``

                .. extdoclink:: Delete By Query
                    :ref: search/reference/delete_by_query/
        """
        log.debug(f"SearchClient.delete_by_query({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/delete_by_query", data=data)

    def batch_delete_by_subject(
        self,
        index_id: UUIDLike,
        subjects: t.Iterable[str],
        additional_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete data in a Search index as an asynchronous task, deleting multiple
        documents based on their ``subject`` values.

        A ``task_id`` value will be included in the response.

        :param index_id: The index in which to delete data
        :param subjects: The subjects to delete, as an iterable of strings
        :param additional_params: Additional parameters to include in the request body

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.batch_delete_by_subject(
                        index_id,
                        subjects=[
                            "very-cool-document",
                            "less-cool-document",
                            "document-wearing-sunglasses",
                        ],
                    )

            .. tab-item:: Example Response Data

                .. expandtestfixture:: search.batch_delete_by_subject

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/batch_delete_by_subject``

                .. extdoclink:: Delete By Subject
                    :ref: search/reference/batch_delete_by_subject/
        """
        log.debug(f"SearchClient.batch_delete_by_subject({index_id}, ...)")
        # convert the provided subjects to a list and use the "safe iter" helper to
        # ensure that a single string is *not* treated as an iterable of strings,
        # which is usually not intentional
        body = {"subjects": list(utils.safe_strseq_iter(subjects))}
        if additional_params:
            body.update(additional_params)
        return self.post(f"/v1/index/{index_id}/batch_delete_by_subject", data=body)

    #
    # Subject Operations
    #

    def get_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Fetch exactly one Subject document from Search, containing one or more Entries.

        :param index_id: the index containing this Subject
        :param subject: the subject string to fetch
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                Fetch the data for subject ``http://example.com/abc`` from index
                ``index_id``:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    subject_data = sc.get_subject(index_id, "http://example.com/abc")

            .. tab-item:: API Info

                ``GET /v1/index/<index_id>/subject``

                .. extdoclink:: Get By Subject
                    :ref: search/reference/get_subject/
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        log.debug(f"SearchClient.get_subject({index_id}, {subject}, ...)")
        return self.get(f"/v1/index/{index_id}/subject", query_params=query_params)

    def delete_subject(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete exactly one Subject document from Search, containing one or more Entries,
        as an asynchronous task.

        A ``task_id`` value will be included in the response.

        :param index_id: the index in which data will be deleted
        :param subject: the subject string for the Subject document to delete
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                Delete all data for subject ``http://example.com/abc`` from index
                ``index_id``, even data which is not visible to the current user:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    response = sc.delete_subject(index_id, "http://example.com/abc")
                    task_id = response["task_id"]

            .. tab-item:: API Info

                ``DELETE /v1/index/<index_id>/subject``

                .. extdoclink:: Delete By Subject
                    :ref: search/reference/delete_subject/
        """
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject

        log.debug(f"SearchClient.delete_subject({index_id}, {subject}, ...)")
        return self.delete(f"/v1/index/{index_id}/subject", query_params=query_params)

    #
    # Entry Operations
    #

    def get_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Fetch exactly one Entry document from Search, identified by the combination of
        ``subject`` string and ``entry_id``, which defaults to ``null``.

        :param index_id: the index containing this Entry
        :param subject: the subject string for the Subject document containing this
            Entry
        :param entry_id: the entry_id for this Entry, which defaults to ``null``
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                Lookup the entry with a subject of ``https://example.com/foo/bar`` and
                a null entry_id:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    entry_data = sc.get_entry(index_id, "http://example.com/foo/bar")

                Lookup the entry with a subject of ``https://example.com/foo/bar`` and
                an entry_id of ``foo/bar``:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    entry_data = sc.get_entry(index_id, "http://example.com/foo/bar", entry_id="foo/bar")

            .. tab-item:: API Info

                ``GET /v1/index/<index_id>/entry``

                .. extdoclink:: Get Entry
                    :ref: search/reference/get_entry/
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id

        log.debug(
            "SearchClient.get_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.get(f"/v1/index/{index_id}/entry", query_params=query_params)

    def create_entry(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        This API method is in effect an alias of ingest and is deprecated.
        Users are recommended to use :meth:`~.ingest` instead.

        Create or update one Entry document in Search.

        The API does not enforce that the document does not exist, and will overwrite
        any existing data.

        :param index_id: the index containing this Entry
        :param data: the entry document to write

        .. tab-set::

            .. tab-item:: Example Usage

                Create an entry with a subject of ``https://example.com/foo/bar`` and
                a null entry_id:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.create_entry(
                        index_id,
                        {
                            "subject": "https://example.com/foo/bar",
                            "visible_to": ["public"],
                            "content": {"foo/bar": "some val"},
                        },
                    )

                Create an entry with a subject of ``https://example.com/foo/bar`` and
                an entry_id of ``foo/bar``:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.create_entry(
                        index_id,
                        {
                            "subject": "https://example.com/foo/bar",
                            "visible_to": ["public"],
                            "id": "foo/bar",
                            "content": {"foo/bar": "some val"},
                        },
                    )

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/entry``

                .. extdoclink:: Create Entry
                    :ref: search/reference/create_or_update_entry/
        """
        warn_deprecated(
            "SearchClient.create_entry is deprecated. "
            "Users should prefer using `SearchClient.ingest`"
        )
        log.debug(f"SearchClient.create_entry({index_id}, ...)")
        return self.post(f"/v1/index/{index_id}/entry", data=data)

    def update_entry(
        self, index_id: UUIDLike, data: dict[str, t.Any]
    ) -> response.GlobusHTTPResponse:
        """
        This API method is in effect an alias of ingest and is deprecated.
        Users are recommended to use :meth:`~.ingest` instead.

        Create or update one Entry document in Search.

        This does not do a partial update, but replaces the existing document.

        :param index_id: the index containing this Entry
        :param data: the entry document to write

        .. tab-set::

            .. tab-item:: Example Usage

                Update an entry with a subject of ``https://example.com/foo/bar`` and
                a null entry_id:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.update_entry(
                        index_id,
                        {
                            "subject": "https://example.com/foo/bar",
                            "visible_to": ["public"],
                            "content": {"foo/bar": "some val"},
                        },
                    )

            .. tab-item:: API Info

                ``PUT /v1/index/<index_id>/entry``

                .. extdoclink:: Update Entry
                    :ref: search/reference/create_or_update_entry/
        """
        warn_deprecated(
            "SearchClient.update_entry is deprecated. "
            "Users should prefer using `SearchClient.ingest`"
        )
        log.debug(f"SearchClient.update_entry({index_id}, ...)")
        return self.put(f"/v1/index/{index_id}/entry", data=data)

    def delete_entry(
        self,
        index_id: UUIDLike,
        subject: str,
        *,
        entry_id: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete exactly one Entry document in Search as an asynchronous task.

        A ``task_id`` value will be included in the response.

        :param index_id: the index in which data will be deleted
        :param subject: the subject string for the Subject of the document to delete
        :param entry_id: the ID string for the Entry to delete
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                Delete an entry with a subject of ``https://example.com/foo/bar`` and
                a null entry_id:

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.delete_entry(index_id, "https://example.com/foo/bar")

                Delete an entry with a subject of ``https://example.com/foo/bar`` and
                an entry_id of "foo/bar":

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    sc.delete_entry(index_id, "https://example.com/foo/bar", entry_id="foo/bar")

            .. tab-item:: API Info

                ``DELETE  /v1/index/<index_id>/entry``

                .. extdoclink:: Delete Entry
                    :ref: search/reference/delete_entry/
        """  # noqa: E501
        if query_params is None:
            query_params = {}
        query_params["subject"] = subject
        if entry_id is not None:
            query_params["entry_id"] = entry_id
        log.debug(
            "SearchClient.delete_entry({}, {}, {}, ...)".format(
                index_id, subject, entry_id
            )
        )
        return self.delete(f"/v1/index/{index_id}/entry", query_params=query_params)

    #
    # Task Management
    #

    def get_task(
        self,
        task_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Fetch a Task document by ID, getting task details and status.

        :param task_id: the task ID from the original task submission
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    task = sc.get_task(task_id)
                    assert task["index_id"] == known_index_id
                    print(task["task_id"], "|", task["state"])

            .. tab-item:: API Info

                ``GET /v1/task/<task_id>``

                .. extdoclink:: Get Task
                    :ref: search/reference/get_task/
        """
        log.debug(f"SearchClient.get_task({task_id})")
        return self.get(f"/v1/task/{task_id}", query_params=query_params)

    def get_task_list(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Fetch a list of recent Task documents for an index, getting task details and
        status.

        :param index_id: the index to query
        :param query_params: additional parameters to pass as query params

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    sc = globus_sdk.SearchClient(...)
                    task_list = sc.get_task_list(index_id)
                    for task in task_list["tasks"]:
                        print(task["task_id"], "|", task["state"])

            .. tab-item:: API Info

                ``GET /v1/task_list/<index_id>``

                .. extdoclink:: Task List
                    :ref: search/reference/task_list/
        """
        log.debug(f"SearchClient.get_task_list({index_id})")
        return self.get(f"/v1/task_list/{index_id}", query_params=query_params)

    #
    # Role Management
    #

    def create_role(
        self,
        index_id: UUIDLike,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Create a new role on an index. You must already have the ``owner`` or
        ``admin`` role on an index to create additional roles.

        Roles are specified as a role name (one of ``"owner"``, ``"admin"``, or
        ``"writer"``) and a `Principal URN
        <https://docs.globus.org/api/search/overview/#principal_urns>`_.

        :param index_id: The index on which to create the role
        :param data: The partial role document to use for creation
        :param query_params: Any additional query params to pass

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    identity_id = "46bd0f56-e24f-11e5-a510-131bef46955c"
                    sc = globus_sdk.SearchClient(...)
                    sc.create_role(
                        index_id,
                        {"role_name": "writer", "principal": f"urn:globus:auth:identity:{identity_id}"},
                    )

            .. tab-item:: API Info

                ``POST /v1/index/<index_id>/role``

                .. extdoclink:: Create Role
                    :ref: search/reference/role_create/
        """  # noqa: E501
        log.debug("SearchClient.create_role(%s, ...)", index_id)
        return self.post(
            f"/v1/index/{index_id}/role", data=data, query_params=query_params
        )

    def get_role_list(
        self,
        index_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        List all roles on an index. You must have the ``owner`` or ``admin``
        role on an index to list roles.

        :param index_id: The index on which to list roles
        :param query_params: Any additional query params to pass

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v1/index/<index_id>/role_list``

                .. extdoclink:: Get Role List
                    :ref: search/reference/role_list/
        """
        log.debug("SearchClient.get_role_list(%s)", index_id)
        return self.get(f"/v1/index/{index_id}/role_list", query_params=query_params)

    def delete_role(
        self,
        index_id: UUIDLike,
        role_id: str,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a role from an index. You must have the ``owner`` or ``admin``
        role on an index to delete roles. You cannot remove the last ``owner`` from an
        index.

        :param index_id: The index from which to delete a role
        :param role_id: The role to delete
        :param query_params: Any additional query params to pass

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /v1/index/<index_id>/role/<role_id>``

                .. extdoclink:: Role Delete
                    :ref: search/reference/role_delete/
        """
        log.debug("SearchClient.delete_role(%s, %s)", index_id, role_id)
        return self.delete(
            f"/v1/index/{index_id}/role/{role_id}", query_params=query_params
        )
