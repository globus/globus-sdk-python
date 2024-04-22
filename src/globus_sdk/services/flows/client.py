from __future__ import annotations

import logging
import typing as t

from globus_sdk import GlobusHTTPResponse, client, paging, scopes, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.scopes import ScopeBuilder
from globus_sdk.utils import MISSING, MissingType

from .errors import FlowsAPIError
from .response import (
    IterableFlowsResponse,
    IterableRunLogsResponse,
    IterableRunsResponse,
)
from .scopes import SpecificFlowScopesClassStub

log = logging.getLogger(__name__)


class FlowsClient(client.BaseClient):
    r"""
    Client for the Globus Flows API.

    .. automethodlist:: globus_sdk.FlowsClient
    """

    error_class = FlowsAPIError
    service_name = "flows"
    scopes = scopes.FlowsScopes

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
        subscription_id: UUIDLike | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Create a flow

        :param title: A non-unique, human-friendly name used for displaying the
            flow to end users. (1 - 128 characters)
        :param definition: JSON object specifying flows states and execution order. For
            a more detailed explanation of the flow definition, see
            `Authoring Flows <https://docs.globus.org/api/flows/authoring-flows>`_
        :param input_schema: A JSON Schema to which flow run input must conform
        :param subtitle: A concise summary of the flow’s purpose. (0 - 128 characters)
        :param description: A detailed description of the flow's purpose for end user
            display. (0 - 4096 characters)
        :param flow_viewers: A set of Principal URN values, or the value "public",
            indicating entities who can view the flow

            .. dropdown:: Example Values

                .. code-block:: json

                    [ "public" ]

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]


        :param flow_starters: A set of Principal URN values, or the value
            "all_authenticated_users", indicating entities who can initiate a *run* of
            the flow

            .. dropdown:: Example Values

                .. code-block:: json

                    [ "all_authenticated_users" ]


                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param flow_administrators: A set of Principal URN values indicating entities
            who can perform administrative operations on the flow (create, delete,
            update)

            .. dropdown:: Example Values

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param keywords: A set of terms used to categorize the flow used in query and
            discovery operations (0 - 1024 items)
        :param subscription_id: The ID of the subscription to associate with the flow,
            marking as a subscription tier flow.
        :param additional_fields: Additional Key/Value pairs sent to the create API

        .. tab-set::

            .. tab-item:: Example Usage

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

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.create_flow

            .. tab-item:: API Info

                .. extdoclink:: Create Flow
                    :service: flows
                    :ref: Flows/paths/~1flows/post
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
                "subscription_id": subscription_id,
            }.items()
            if v is not None
        }
        data.update(additional_fields or {})

        return self.post("/flows", data=data)

    def get_flow(
        self,
        flow_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """Retrieve a flow by ID

        :param flow_id: The ID of the flow to fetch
        :param query_params: Any additional parameters to be passed through
            as query params.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Flow
                    :service: flows
                    :ref: Flows/paths/~1flows~1{flow_id}/get
        """

        if query_params is None:
            query_params = {}

        return self.get(f"/flows/{flow_id}", query_params=query_params)

    @paging.has_paginator(paging.MarkerPaginator, items_key="flows")
    def list_flows(
        self,
        *,
        filter_role: str | None = None,
        filter_fulltext: str | None = None,
        orderby: str | t.Iterable[str] | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableFlowsResponse:
        """
        List deployed flows

        :param filter_role: A role name specifying the minimum permissions required for
            a flow to be included in the response.
        :param filter_fulltext: A string to use in a full-text search to filter results
        :param orderby: A criterion for ordering flows in the listing
        :param marker: A marker for pagination
        :param query_params: Any additional parameters to be passed through
            as query params.

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
        times, getting the most recently updated flow first. Multiple ``orderby`` values
        may be given as an iterable, e.g. ``orderby=["updated_at DESC", "title ASC"]``.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    import json
                    import textwrap

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    my_frobulate_flows = flows.list_flows(
                        filter_role="flow_owner",
                        filter_fulltext="frobulate",
                        orderby=("title ASC", "updated_at DESC"),
                    )
                    for flow_doc in my_frobulate_flows:
                        print(f"Title: {flow_doc['title']}")
                        print(f"Description: {flow_doc['description']}")
                        print("Definition:")
                        print(
                            textwrap.indent(
                                json.dumps(
                                    flow_doc["definition"],
                                    indent=2,
                                    separators=(",", ": "),
                                ),
                                "    ",
                            )
                        )
                        print()

            .. tab-item:: Paginated Usage

                .. paginatedusage:: list_flows

            .. tab-item:: API Info

                .. extdoclink:: List Flows
                    :service: flows
                    :ref: Flows/paths/~1flows/get
        """

        if query_params is None:
            query_params = {}
        if filter_role is not None:
            query_params["filter_role"] = filter_role
        if filter_fulltext is not None:
            query_params["filter_fulltext"] = filter_fulltext
        if orderby is not None:
            if isinstance(orderby, str):
                query_params["orderby"] = orderby
            else:
                # copy any input sequence to force the type to `list` which is known to
                # behave well
                # this also ensures that we will consume non-sequence iterables
                # (e.g. generator expressions) in a well-defined way
                query_params["orderby"] = list(orderby)
        if marker is not None:
            query_params["marker"] = marker

        return IterableFlowsResponse(self.get("/flows", query_params=query_params))

    def update_flow(
        self,
        flow_id: UUIDLike,
        *,
        title: str | None = None,
        definition: dict[str, t.Any] | None = None,
        input_schema: dict[str, t.Any] | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        flow_owner: str | None = None,
        flow_viewers: list[str] | None = None,
        flow_starters: list[str] | None = None,
        flow_administrators: list[str] | None = None,
        keywords: list[str] | None = None,
        subscription_id: UUIDLike | t.Literal["DEFAULT"] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Update a flow

        Only the parameter `flow_id` is required.
        Any fields omitted from the request will be unchanged

        :param flow_id: The ID of the flow to fetch
        :param title: A non-unique, human-friendly name used for displaying the
            flow to end users. (1 - 128 characters)
        :param definition: JSON object specifying flows states and execution order. For
            a more detailed explanation of the flow definition, see
            `Authoring Flows <https://docs.globus.org/api/flows/authoring-flows>`_
        :param input_schema: A JSON Schema to which flow run input must conform
        :param subtitle: A concise summary of the flow’s purpose. (0 - 128 characters)
        :param description: A detailed description of the flow's purpose for end user
            display. (0 - 4096 characters)
        :param flow_owner: An Auth Identity URN to set as flow owner; this must match
            the Identity URN of the entity calling `update_flow`
        :param flow_viewers: A set of Principal URN values, or the value "public",
            indicating entities who can view the flow

            .. dropdown:: Example Values

                .. code-block:: json

                    [ "public" ]

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param flow_starters: A set of Principal URN values, or the value
            "all_authenticated_users", indicating entities who can initiate a *run* of
            the flow

            .. dropdown:: Example Values

                .. code-block:: json

                    [ "all_authenticated_users" ]


                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param flow_administrators: A set of Principal URN values indicating entities
            who can perform administrative operations on the flow (create, delete,
            update)

            .. dropdown:: Example Value

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param keywords: A set of terms used to categorize the flow used in query and
            discovery operations (0 - 1024 items)
        :param subscription_id: A subscription ID to assign to the flow.
        :param additional_fields: Additional Key/Value pairs sent to the create API

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.update_flow(
                        flow_id="581753c7-45da-43d3-ad73-246b46e7cb6b",
                        keywords=["new", "overriding", "keywords"],
                    )

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.update_flow

            .. tab-item:: API Info

                .. extdoclink:: Update Flow
                    :service: flows
                    :ref: Flows/paths/~1flows~1{flow_id}/put
        """  # noqa E501

        data = {
            k: v
            for k, v in {
                "title": title,
                "definition": definition,
                "input_schema": input_schema,
                "subtitle": subtitle,
                "description": description,
                "flow_owner": flow_owner,
                "flow_viewers": flow_viewers,
                "flow_starters": flow_starters,
                "flow_administrators": flow_administrators,
                "keywords": keywords,
                "subscription_id": subscription_id,
            }.items()
            if v is not None and v is not MISSING
        }
        data.update(additional_fields or {})

        return self.put(f"/flows/{flow_id}", data=data)

    def delete_flow(
        self,
        flow_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """Delete a flow

        :param flow_id: The ID of the flow to delete
        :param query_params: Any additional parameters to be passed through
            as query params.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Delete Flow
                    :service: flows
                    :ref: Flows/paths/~1flows~1{flow_id}/delete
        """

        if query_params is None:
            query_params = {}

        return self.delete(f"/flows/{flow_id}", query_params=query_params)

    def validate_flow(
        self,
        definition: dict[str, t.Any],
        input_schema: dict[str, t.Any] | MissingType = MISSING,
    ) -> GlobusHTTPResponse:
        """
        Validate a flow

        :param definition: JSON object specifying flow states and execution order. For
            a more detailed explanation of the flow definition, see
            `Authoring Flows <https://docs.globus.org/api/flows/authoring-flows>`_
        :param input_schema: A JSON Schema to which flow run input must conform

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    ...
                    flows = FlowsClient(...)
                    flows.validate_flow(
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

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.validate_flow

            .. tab-item:: API Info

                .. extdoclink:: Validate Flow
                    :service: flows
                    :ref: Flows/paths/~1flows~1validate/post
        """  # noqa E501

        data = {"definition": definition, "input_schema": input_schema}
        return self.post("/flows/validate", data=data)

    @paging.has_paginator(paging.MarkerPaginator, items_key="runs")
    def list_runs(
        self,
        *,
        filter_flow_id: t.Iterable[UUIDLike] | UUIDLike | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableRunsResponse:
        """
        List all runs.

        :param filter_flow_id: One or more flow IDs used to filter the results
        :param marker: A pagination marker, used to get the next page of results.
        :param query_params: Any additional parameters to be passed through

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    flows = globus_sdk.FlowsClient(...)
                    for run in flows.list_runs():
                        print(run["run_id"])

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.list_runs

            .. tab-item:: API Info

                .. extdoclink:: List Runs
                    :service: flows
                    :ref: Runs/paths/~1runs/get
        """
        if query_params is None:
            query_params = {}
        if filter_flow_id is not None:
            query_params["filter_flow_id"] = ",".join(
                utils.safe_strseq_iter(filter_flow_id)
            )
        if marker is not None:
            query_params["marker"] = marker
        return IterableRunsResponse(self.get("/runs", query_params=query_params))

    @paging.has_paginator(paging.MarkerPaginator, items_key="entries")
    def get_run_logs(
        self,
        run_id: UUIDLike,
        *,
        limit: int | None = None,
        reverse_order: bool | None = None,
        marker: str | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableRunLogsResponse:
        """
        Retrieve the execution logs associated with a run

        These logs describe state transitions and associated payloads for a run

        :param run_id: Run ID to retrieve logs for
        :param limit: Maximum number of log entries to return (server default: 10)
             (value between 1 and 100 inclusive)
        :param reverse_order: Return results in reverse chronological order (server
            default: false)
        :param marker: Marker for the next page of results (provided by the server)
        :param query_params: Any additional parameters to be passed through

        .. tab-set::

            .. tab-item:: Paginated Usage

                .. paginatedusage:: get_run_logs

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.get_run_logs

            .. tab-item:: API Info

                .. extdoclink:: Get Run Logs
                    :service: flows
                    :ref: Runs/paths/~1runs~1{action_id}~1log/get
        """

        query_params = {
            "limit": limit,
            "reverse_order": reverse_order,
            "marker": marker,
            **(query_params or {}),
        }
        # Filter out request keys with None values to allow server defaults
        query_params = {k: v for k, v in query_params.items() if v is not None}
        return IterableRunLogsResponse(
            self.get(f"/runs/{run_id}/log", query_params=query_params)
        )

    def get_run(
        self,
        run_id: UUIDLike,
        *,
        include_flow_description: bool | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Retrieve information about a particular run of a flow

        :param run_id: The ID of the run to get
        :param include_flow_description: If set to true, the lookup will attempt to
           attach metadata about the flow to the run to the run response under the key
           "flow_description" (default: False)
        :param query_params: Any additional parameters to be passed through


        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.get_run("581753c7-45da-43d3-ad73-246b46e7cb6b")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.get_run

            .. tab-item:: API Info

                .. extdoclink:: Get Run
                    :service: flows
                    :ref: Flows/paths/~1runs~1{run_id}/get
        """

        query_params = query_params or {}
        if include_flow_description is not None:
            query_params["include_flow_description"] = include_flow_description

        return self.get(f"/runs/{run_id}", query_params=query_params)

    def get_run_definition(
        self,
        run_id: UUIDLike,
    ) -> GlobusHTTPResponse:
        """
        Get the flow definition and input schema at the time the run was started.

        :param run_id: The ID of the run to get

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.get_run_definition("581753c7-45da-43d3-ad73-246b46e7cb6b")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.get_run_definition

            .. tab-item:: API Info

                .. extdoclink:: Get Run Definition
                    :service: flows
                    :ref: Flows/paths/~1runs~1{run_id}~1definition/get
        """

        return self.get(f"/runs/{run_id}/definition")

    def cancel_run(self, run_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Cancel a run.

        :param run_id: The ID of the run to cancel


        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.cancel_run("581753c7-45da-43d3-ad73-246b46e7cb6b")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.cancel_run

            .. tab-item:: API Info

                .. extdoclink:: Cancel Run
                    :service: flows
                    :ref: Runs/paths/~1runs~1{run_id}~1cancel/post
        """

        return self.post(f"/runs/{run_id}/cancel")

    def update_run(
        self,
        run_id: UUIDLike,
        *,
        label: str | None = None,
        tags: list[str] | None = None,
        run_monitors: list[str] | None = None,
        run_managers: list[str] | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Update the metadata of a specific run.

        :param run_id: The ID of the run to update
        :param label: A short human-readable title (1 - 64 chars)
        :param tags: A collection of searchable tags associated with the run.
            Tags are normalized by stripping leading and trailing whitespace,
            and replacing all whitespace with a single space.
        :param run_monitors: A list of authenticated entities (identified by URN)
            authorized to view this run in addition to the run owner
        :param run_managers: A list of authenticated entities (identified by URN)
            authorized to view & cancel this run in addition to the run owner
        :param additional_fields: Additional Key/Value pairs sent to the run API
            (this parameter is used to bypass local sdk key validation helping)


        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.update_run(
                        "581753c7-45da-43d3-ad73-246b46e7cb6b",
                        label="Crunch numbers for experiment xDA202-batch-10",
                    )

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.update_run

            .. tab-item:: API Info

                .. extdoclink:: Update Run
                    :service: flows
                    :ref: Runs/paths/~1runs~1{run_id}/put
        """

        data = {
            k: v
            for k, v in {
                "tags": tags,
                "label": label,
                "run_monitors": run_monitors,
                "run_managers": run_managers,
            }.items()
            if v is not None
        }
        data.update(additional_fields or {})

        return self.put(f"/runs/{run_id}", data=data)

    def delete_run(self, run_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a run.

        :param run_id: The ID of the run to delete


        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import FlowsClient

                    flows = FlowsClient(...)
                    flows.delete_run("581753c7-45da-43d3-ad73-246b46e7cb6b")

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.delete_run

            .. tab-item:: API Info

                .. extdoclink:: Delete Run
                    :service: flows
                    :ref: Runs/paths/~1runs~1{run_id}~1release/post
        """

        return self.post(f"/runs/{run_id}/release")


class SpecificFlowClient(client.BaseClient):
    r"""
    Client for interacting with a specific flow through the Globus Flows API.

    Unlike other client types, this must be provided with a specific flow id. All other
        arguments are the same as those for :class:`~globus_sdk.BaseClient`.

    :param flow_id: The generated UUID associated with a flow

    .. automethodlist:: globus_sdk.SpecificFlowClient
    """

    error_class = FlowsAPIError
    service_name = "flows"
    scopes: ScopeBuilder = SpecificFlowScopesClassStub()

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
        :param label: A short human-readable title (1 - 64 chars)
        :param tags: A collection of searchable tags associated with the run. Tags are
            normalized by stripping leading and trailing whitespace, and replacing all
            whitespace with a single space.
        :param run_monitors: A list of authenticated entities (identified by URN)
            authorized to view this run in addition to the run owner
        :param run_managers: A list of authenticated entities (identified by URN)
            authorized to view & cancel this run in addition to the run owner
        :param additional_fields: Additional Key/Value pairs sent to the run API
            (this parameter is used to bypass local sdk key validation helping)

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Run Flow
                    :service: flows
                    :ref: ~1flows~1{flow_id}~1run/post
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

    def resume_run(self, run_id: UUIDLike) -> GlobusHTTPResponse:
        """
        :param run_id: The ID of the run to resume

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import SpecificFlowClient

                    ...
                    flow = SpecificFlowClient(flow_id, ...)
                    flow.resume_run(run_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.resume_run

            .. tab-item:: API Info

                .. extdoclink:: Resume Run
                    :service: flows
                    :ref: Runs/paths/~1flows~1{flow_id}~1runs~1{run_id}~1resume/post
        """
        return self.post(f"/runs/{run_id}/resume")
