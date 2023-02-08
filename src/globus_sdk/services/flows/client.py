from __future__ import annotations

import logging
import typing as t

from globus_sdk import GlobusHTTPResponse, client, paging, scopes, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.scopes import ScopeBuilder

from .errors import FlowsAPIError
from .response import IterableFlowsResponse

log = logging.getLogger(__name__)

C = t.TypeVar("C", bound=t.Callable[..., t.Any])


def _flowdoc(message: str, link: str) -> t.Callable[[C], C]:
    # do not use functools.partial because it doesn't preserve type information
    # see: https://github.com/python/mypy/issues/1484
    def partial(func: C) -> C:
        return utils.doc_api_method(
            message,
            link,
            external_base_url="https://globusonline.github.io/flows#tag",
        )(func)

    return partial


class FlowsClient(client.BaseClient):
    r"""
    Client for the Globus Flows API.

    .. automethodlist:: globus_sdk.FlowsClient
    """
    error_class = FlowsAPIError
    service_name = "flows"
    scopes = scopes.FlowsScopes

    @_flowdoc("Create Flow", "Flows/paths/~1flows/post")
    def create_flow(
        self,
        title: str,
        definition: dict[str, t.Any],
        input_schema: dict[str, t.Any],
        subtitle: str | None = None,
        description: str | None = None,
        flow_viewers: list[str] | None = None,
        flow_starters: list[str] | None = None,
        flow_administrators: list[str] | None = None,
        keywords: list[str] | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Create a Flow

        Example Usage:

        .. code-block:: python

            from globus_sdk import FlowsClient

            ...
            flows = FlowsClient(...)
            flows.create_flow(
                title="my-cool-flow",
                definition={
                    "StartAt": "the-one-true-state",
                    "States": {"the-one-true-state": {"Type": "Pass", "End": True}},
                },
                input_schema={
                    "type": "object",
                    "properties": {
                        "input-a": {"type": "string"},
                        "input-b": {"type": "number"},
                        "input-c": {"type": "boolean"},
                    },
                },
            )

        :param title: A non-unique, human-friendly name used for displaying the
            flow to end users.
        :type title: str (1 - 128 characters)
        :param definition: JSON object specifying flows states and execution order. For
            a more detailed explanation of the flow definition, see
            `Authoring Flows <https://globus-automate-client.readthedocs.io/en/latest/authoring_flows.html>`_
        :type definition: dict
        :param input_schema: A JSON Schema to which Flow Invocation input must conform
        :type input_schema: dict
        :param subtitle: A concise summary of the flow’s purpose.
        :type subtitle: str (0 - 128 characters), optional
        :param description: A detailed description of the flow's purpose for end user
            display.
        :type description: str (0 - 4096 characters), optional
        :param flow_viewers: A set of Principal URN values, or the value "public"
            indicating entities who can view the flow

            Examples:

            .. code-block:: json

                [ "public" ]

            .. code-block:: json

                [
                    "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                    "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                ]


        :type flow_viewers: list[str], optional
        :param flow_starters: A set of Principal URN values, or the value
            "all_authenticated_users" indicating entities who can initiate a *Run* of
            the flow

            Examples:

            .. code-block:: json

                [ "all_authenticated_users" ]


            .. code-block:: json

                [
                    "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                    "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                ]

        :type flow_starters: list[str], optional
        :param flow_administrators: A set of Principal URN values indicating entities
            who can perform administrative operations on the flow (create, delete,
            update)

            Example:

            .. code-block:: json

                [
                    "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                    "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                ]

        :type flow_administrators: list[str], optional
        :param keywords: A set of terms used to categorize the flow used in query and
            discovery operations
        :type keywords: list[str] (0 - 1024 items), optional
        :param additional_fields: Additional Key/Value pairs sent to the create API
        :type additional_fields: dict or str -> any, optional
        """  # noqa E501

        data = {
            k: v
            for k, v in {
                "title": title,
                "definition": definition,
                "input_schema": input_schema,
                "subtitle": subtitle,
                "description": description,
                "flow_viewers": flow_viewers,
                "flow_starters": flow_starters,
                "flow_administrators": flow_administrators,
                "keywords": keywords,
            }.items()
            if v is not None
        }
        data.update(additional_fields or {})

        return self.post("/flows", data=data)

    @_flowdoc("Get Flow", "Flows/paths/~1flows~1{flow_id}/get")
    def get_flow(
        self,
        flow_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """Retrieve a Flow by ID

        :param flow_id: The ID of the Flow to fetch
        :type flow_id: str or UUID
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional
        """

        if query_params is None:
            query_params = {}

        return self.get(f"/flows/{flow_id}", query_params=query_params)

    @_flowdoc("List Flows", "Flows/paths/~1flows/get")
    @paging.has_paginator(paging.MarkerPaginator, items_key="flows")
    def list_flows(
        self,
        *,
        filter_role: str | None = None,
        filter_fulltext: str | None = None,
        orderby: str | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableFlowsResponse:
        """
        List deployed Flows

        :param filter_role: A role name specifying the minimum permissions required for
            a Flow to be included in the response.
        :type filter_role: str, optional
        :param filter_fulltext: A string to use in a full-text search to filter results
        :type filter_fulltext: str, optional
        :param orderby: A criterion for ordering flows in the listing
        :type orderby: str, optional
        :param marker: A marker for pagination
        :type marker: str, optional
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        **Role Values**

        The valid values for ``role`` are, in order of precedence for ``filter_role``:

          - ``flow_viewer``
          - ``flow_starter``
          - ``flow_administrator``
          - ``flow_owner``

        For example, if ``flow_starter`` is specified then flows for which the user has
        the ``flow_starter``, ``flow_administrator`` or ``flow_owner`` roles will be
        returned.

        **OrderBy Values**

        Values for ``orderby`` consist of a field name, a space, and an
        ordering mode -- ``ASC`` for "ascending" and ``DESC`` for "descending".

        Supported field names are

          - ``id``
          - ``scope_string``
          - ``flow_owners``
          - ``flow_administrators``
          - ``title``
          - ``created_at``
          - ``updated_at``

        For example, ``orderby="updated_at DESC"`` requests a descending sort on update
        times, getting the most recently updated flow first.
        """

        if query_params is None:
            query_params = {}
        if filter_role is not None:
            query_params["filter_role"] = filter_role
        if filter_fulltext is not None:
            query_params["filter_fulltext"] = filter_fulltext
        if orderby is not None:
            query_params["orderby"] = orderby
        if marker is not None:
            query_params["marker"] = marker

        return IterableFlowsResponse(self.get("/flows", query_params=query_params))

    @_flowdoc("Delete Flow", "Flows/paths/~1flows~1{flow_id}/delete")
    def delete_flow(
        self,
        flow_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """Delete a Flow

        :param flow_id: The ID of the flow to delete
        :type flow_id: str or UUID, optional
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional
        """

        if query_params is None:
            query_params = {}

        return self.delete(f"/flows/{flow_id}", query_params=query_params)


class SpecificFlowClient(client.BaseClient):
    r"""
    Client for interacting with a specific Globus Flow through the Flows API.

    Unlike other client types, this must be provided with a specific flow id. All other
        arguments are the same as those for `~globus_sdk.BaseClient`.

    :param flow_id: The generated UUID associated with a flow
    :type flow_id: str or uuid

    .. automethodlist:: globus_sdk.SpecificFlowClient
    """

    error_class = FlowsAPIError
    service_name = "flows"

    def __init__(
        self,
        flow_id: UUIDLike,
        *,
        environment: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ):
        super().__init__(
            environment=environment,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )
        self._flow_id = flow_id
        user_scope_value = f"flow_{str(flow_id).replace('-', '_')}_user"
        self.scopes = ScopeBuilder(
            resource_server=str(self._flow_id),
            known_url_scopes=[("user", user_scope_value)],
        )

    @_flowdoc("Run Flow", "~1flows~1{flow_id}~1run/post")
    def run_flow(
        self,
        body: dict[str, t.Any],
        *,
        label: str | None = None,
        tags: list[str] | None = None,
        run_monitors: list[str] | None = None,
        run_managers: list[str] | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """

        :param body: The input json object handed to the first flow state. The flows
            service will validate this object against the flow's supplied input schema.
        :type body: json dict
        :param label: A short human-readable title
        :type label: Optional string (0 - 64 chars)
        :param tags: A collection of searchable tags associated with the run. Tags are
            normalized by stripping leading and trailing whitespace, and replacing all
            whitespace with a single space.
        :type tags: Optional list of strings
        :param run_monitors: A list of authenticated entities (identified by URN)
            authorized to view this run in addition to the run owner
        :type run_monitors: Optional list of strings
        :param run_managers: A list of authenticated entities (identified by URN)
            authorized to view & cancel this run in addition to the run owner
        :type run_managers: Optional list of strings
        :param additional_fields: Additional Key/Value pairs sent to the run API
            (this parameter is used to bypass local sdk key validation helping)
        :type additional_fields: Optional dictionary
        """
        data = {
            k: v
            for k, v in {
                "body": body,
                "tags": tags,
                "label": label,
                "run_monitors": run_monitors,
                "run_managers": run_managers,
            }.items()
            if v is not None
        }
        data.update(additional_fields or {})

        return self.post(f"/flows/{self._flow_id}/run", data=data)
