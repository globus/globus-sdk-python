from __future__ import annotations

import logging
import sys
import typing as t
import uuid

from globus_sdk import GlobusHTTPResponse, client, paging
from globus_sdk._internal import guards
from globus_sdk._internal.remarshal import commajoin
from globus_sdk._missing import MISSING, MissingType
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.globus_app import GlobusApp
from globus_sdk.scopes import (
    FlowsScopes,
    GCSCollectionScopes,
    Scope,
    SpecificFlowScopes,
    TransferScopes,
)
from globus_sdk.transport import RequestsTransport, RetryConfig

from .data import RunActivityNotificationPolicy
from .errors import FlowsAPIError
from .response import (
    IterableFlowsResponse,
    IterableRunLogsResponse,
    IterableRunsResponse,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

log = logging.getLogger(__name__)


class FlowsClient(client.BaseClient):
    r"""
    Client for the Globus Flows API.

    .. sdk-sphinx-copy-params:: BaseClient

    .. automethodlist:: globus_sdk.FlowsClient
    """

    error_class = FlowsAPIError
    service_name = "flows"
    scopes = FlowsScopes
    default_scope_requirements = [FlowsScopes.all]

    def create_flow(
        self,
        title: str,
        definition: dict[str, t.Any],
        input_schema: dict[str, t.Any],
        subtitle: str | MissingType = MISSING,
        description: str | MissingType = MISSING,
        flow_viewers: list[str] | MissingType = MISSING,
        flow_starters: list[str] | MissingType = MISSING,
        flow_administrators: list[str] | MissingType = MISSING,
        run_managers: list[str] | MissingType = MISSING,
        run_monitors: list[str] | MissingType = MISSING,
        keywords: list[str] | MissingType = MISSING,
        subscription_id: uuid.UUID | str | None | MissingType = MISSING,
        authentication_policy_id: uuid.UUID | str | None | MissingType = MISSING,
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

        :param run_managers: A set of Principal URN values indicating entities who can
            perform management operations on the flow's *runs*.

            .. dropdown:: Example Values

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param run_monitors: A set of Principal URN values indicating entities who can
            monitor the flow's *runs*.

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
        :param authentication_policy_id: The ID of the authentication policy to associate
             with the flow.
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
            "title": title,
            "definition": definition,
            "input_schema": input_schema,
            "subtitle": subtitle,
            "description": description,
            "flow_viewers": flow_viewers,
            "flow_starters": flow_starters,
            "flow_administrators": flow_administrators,
            "run_managers": run_managers,
            "run_monitors": run_monitors,
            "keywords": keywords,
            "subscription_id": subscription_id,
            "authentication_policy_id": authentication_policy_id,
            **(additional_fields or {}),
        }
        return self.post("/flows", data=data)

    def get_flow(
        self,
        flow_id: uuid.UUID | str,
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
        return self.get(f"/flows/{flow_id}", query_params=query_params)

    @paging.has_paginator(paging.MarkerPaginator, items_key="flows")
    def list_flows(
        self,
        *,
        filter_roles: str | t.Iterable[str] | MissingType = MISSING,
        filter_fulltext: str | MissingType = MISSING,
        orderby: str | t.Iterable[str] | MissingType = MISSING,
        marker: str | MissingType = MISSING,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableFlowsResponse:
        """
        List deployed flows

        :param filter_roles: A list of role names specifying the roles the user must
            have for a flow to be included in the response.
        :param filter_fulltext: A string to use in a full-text search to filter results
        :param orderby: A criterion for ordering flows in the listing
        :param marker: A marker for pagination
        :param query_params: Any additional parameters to be passed through
            as query params.

        **Role Filters**

        ``filter_roles`` accepts a list of roles which are used to filter the results to
        flows where the caller has any of the specified roles.

        The valid role values are:

        - ``flow_viewer``
        - ``flow_starter``
        - ``flow_administrator``
        - ``flow_owner``
        - ``run_monitor``
        - ``run_manager``

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
                        filter_roles="flow_owner",
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
        query_params = {
            "filter_roles": commajoin(filter_roles),
            "filter_fulltext": filter_fulltext,
            # if `orderby` is an iterable (e.g., generator expression), it gets
            # converted to a list in this step
            "orderby": (
                orderby if isinstance(orderby, (str, MissingType)) else list(orderby)
            ),
            "marker": marker,
            **(query_params or {}),
        }
        return IterableFlowsResponse(self.get("/flows", query_params=query_params))

    def update_flow(
        self,
        flow_id: uuid.UUID | str,
        *,
        title: str | MissingType = MISSING,
        definition: dict[str, t.Any] | MissingType = MISSING,
        input_schema: dict[str, t.Any] | MissingType = MISSING,
        subtitle: str | MissingType = MISSING,
        description: str | MissingType = MISSING,
        flow_owner: str | MissingType = MISSING,
        flow_viewers: list[str] | MissingType = MISSING,
        flow_starters: list[str] | MissingType = MISSING,
        flow_administrators: list[str] | MissingType = MISSING,
        run_managers: list[str] | MissingType = MISSING,
        run_monitors: list[str] | MissingType = MISSING,
        keywords: list[str] | MissingType = MISSING,
        subscription_id: uuid.UUID | str | t.Literal["DEFAULT"] | MissingType = MISSING,
        authentication_policy_id: uuid.UUID | str | MissingType = MISSING,
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

        :param run_managers: A set of Principal URN values indicating entities who can
            perform management operations on the flow's *runs*.

            .. dropdown:: Example Values

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param run_monitors: A set of Principal URN values indicating entities who can
            monitor the flow's *runs*.

            .. dropdown:: Example Values

                .. code-block:: json

                    [
                        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
                        "urn:globus:groups:id:c1dcd951-3f35-4ea3-9f28-a7cdeaf8b68f"
                    ]

        :param keywords: A set of terms used to categorize the flow used in query and
            discovery operations (0 - 1024 items)
        :param subscription_id: A subscription ID to assign to the flow.
        :param authentication_policy_id: An authentication policy to assign to the flow.
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
            "title": title,
            "definition": definition,
            "input_schema": input_schema,
            "subtitle": subtitle,
            "description": description,
            "flow_owner": flow_owner,
            "flow_viewers": flow_viewers,
            "flow_starters": flow_starters,
            "flow_administrators": flow_administrators,
            "run_managers": run_managers,
            "run_monitors": run_monitors,
            "keywords": keywords,
            "subscription_id": subscription_id,
            "authentication_policy_id": authentication_policy_id,
            **(additional_fields or {}),
        }
        return self.put(f"/flows/{flow_id}", data=data)

    def delete_flow(
        self,
        flow_id: uuid.UUID | str,
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

        data = {
            "definition": definition,
            "input_schema": input_schema,
        }
        return self.post("/flows/validate", data=data)

    @paging.has_paginator(paging.MarkerPaginator, items_key="runs")
    def list_runs(
        self,
        *,
        filter_flow_id: (
            t.Iterable[uuid.UUID | str] | uuid.UUID | str | MissingType
        ) = MISSING,
        filter_roles: str | t.Iterable[str] | MissingType = MISSING,
        marker: str | MissingType = MISSING,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableRunsResponse:
        """
        List all runs.

        :param filter_flow_id: One or more flow IDs used to filter the results
        :param filter_roles: A list of role names used to filter the results
        :param marker: A pagination marker, used to get the next page of results.
        :param query_params: Any additional parameters to be passed through

        **Filter Roles Values**

        The valid values for ``role`` are:

          - ``run_owner``
          - ``run_manager``
          - ``run_monitor``
          - ``flow_run_manager``
          - ``flow_run_monitor``

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
        query_params = {
            "filter_flow_id": commajoin(filter_flow_id),
            "filter_roles": commajoin(filter_roles),
            "marker": marker,
            **(query_params or {}),
        }
        return IterableRunsResponse(self.get("/runs", query_params=query_params))

    @paging.has_paginator(paging.MarkerPaginator, items_key="entries")
    def get_run_logs(
        self,
        run_id: uuid.UUID | str,
        *,
        limit: int | MissingType = MISSING,
        reverse_order: bool | MissingType = MISSING,
        marker: str | MissingType = MISSING,
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
        return IterableRunLogsResponse(
            self.get(f"/runs/{run_id}/log", query_params=query_params)
        )

    def get_run(
        self,
        run_id: uuid.UUID | str,
        *,
        include_flow_description: bool | MissingType = MISSING,
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
        query_params = {
            "include_flow_description": include_flow_description,
            **(query_params or {}),
        }
        return self.get(f"/runs/{run_id}", query_params=query_params)

    def get_run_definition(
        self,
        run_id: uuid.UUID | str,
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

    def cancel_run(self, run_id: uuid.UUID | str) -> GlobusHTTPResponse:
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
        run_id: uuid.UUID | str,
        *,
        label: str | MissingType = MISSING,
        tags: list[str] | MissingType = MISSING,
        run_monitors: list[str] | MissingType = MISSING,
        run_managers: list[str] | MissingType = MISSING,
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
            "tags": tags,
            "label": label,
            "run_monitors": run_monitors,
            "run_managers": run_managers,
            **(additional_fields or {}),
        }
        return self.put(f"/runs/{run_id}", data=data)

    def delete_run(self, run_id: uuid.UUID | str) -> GlobusHTTPResponse:
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

    .. sdk-sphinx-copy-params:: BaseClient

        :param flow_id: The generated UUID associated with a flow

    .. automethodlist:: globus_sdk.SpecificFlowClient
    """

    error_class = FlowsAPIError
    service_name = "flows"
    scopes: SpecificFlowScopes = SpecificFlowScopes._build_class_stub()

    def __init__(
        self,
        flow_id: uuid.UUID | str,
        *,
        environment: str | None = None,
        app: GlobusApp | None = None,
        app_scopes: list[Scope] | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport: RequestsTransport | None = None,
        retry_config: RetryConfig | None = None,
    ) -> None:
        self._flow_id = flow_id
        self.scopes = SpecificFlowScopes(flow_id)
        super().__init__(
            app=app,
            app_scopes=app_scopes,
            environment=environment,
            authorizer=authorizer,
            app_name=app_name,
            transport=transport,
            retry_config=retry_config,
        )

    @property
    def default_scope_requirements(self) -> list[Scope]:
        return [self.scopes.user]

    def add_app_transfer_data_access_scope(
        self, collection_ids: uuid.UUID | str | t.Iterable[uuid.UUID | str]
    ) -> Self:
        """
        Add a dependent ``data_access`` scope for one or more given ``collection_ids``
        to this client's ``GlobusApp``, under the Transfer ``all`` scope.
        Useful for preventing ``ConsentRequired`` errors when starting or resuming runs
        of flows that use Globus Connect Server mapped collection(s).

        .. warning::

            This method must only be used on ``collection_ids`` for non-High-Assurance
            GCS Mapped Collections.

            Use on other collection types, e.g., on GCP Mapped Collections or any form
            of Guest Collection, will result in "Unknown Scope" errors during the login
            flow.

        Returns ``self`` for chaining.

        Raises ``GlobusSDKUsageError`` if this client was not initialized with an app.

        :param collection_ids: a collection ID or an iterable of IDs.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    flow_id = ...
                    COLLECTION_ID = ...
                    app = UserApp("myapp", client_id=NATIVE_APP_CLIENT_ID)
                    client = SpecificFlowClient(FLOW_ID, app=app).add_app_transfer_data_access_scope(
                        COLLECTION_ID
                    )

                    client.run_flow({"collection": COLLECTION_ID})
        """  # noqa: E501
        if isinstance(collection_ids, (str, uuid.UUID)):
            guards.validators.uuidlike("collection_ids", collection_ids)
            # wrap the collection_ids input in a list for consistent iteration below
            collection_ids_ = [collection_ids]
        else:
            # copy to a list so that ephemeral iterables can be iterated multiple times
            collection_ids_ = list(collection_ids)
            for i, c in enumerate(collection_ids_):
                guards.validators.uuidlike(f"collection_ids[{i}]", c)

        transfer_scope = TransferScopes.all.with_optional(True)
        for coll_id in collection_ids_:
            data_access_scope = GCSCollectionScopes(
                str(coll_id)
            ).data_access.with_optional(True)
            transfer_scope = transfer_scope.with_dependency(data_access_scope)

        specific_flow_scope = self.scopes.user.with_dependency(transfer_scope)
        self.add_app_scope(specific_flow_scope)
        return self

    def run_flow(
        self,
        body: dict[str, t.Any],
        *,
        label: str | MissingType = MISSING,
        tags: list[str] | MissingType = MISSING,
        activity_notification_policy: (
            dict[str, t.Any] | RunActivityNotificationPolicy | MissingType
        ) = MISSING,
        run_monitors: list[str] | MissingType = MISSING,
        run_managers: list[str] | MissingType = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        :param body: The input json object handed to the first flow state. The flows
            service will validate this object against the flow's supplied input schema.
        :param label: A short human-readable title (1 - 64 chars)
        :param tags: A collection of searchable tags associated with the run. Tags are
            normalized by stripping leading and trailing whitespace, and replacing all
            whitespace with a single space.
        :param activity_notification_policy: A policy document which declares when the
            run will send notification emails. By default, notifications are only sent
            when a run status changes to ``"INACTIVE"``.
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
            "body": body,
            "tags": tags,
            "label": label,
            "activity_notification_policy": activity_notification_policy,
            "run_monitors": run_monitors,
            "run_managers": run_managers,
            **(additional_fields or {}),
        }
        return self.post(f"/flows/{self._flow_id}/run", data=data)

    def resume_run(self, run_id: uuid.UUID | str) -> GlobusHTTPResponse:
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

    def validate_run(
        self,
        body: dict[str, t.Any],
        *,
        label: str | MissingType = MISSING,
        tags: list[str] | MissingType = MISSING,
        run_monitors: list[str] | MissingType = MISSING,
        run_managers: list[str] | MissingType = MISSING,
        activity_notification_policy: (
            dict[str, t.Any] | RunActivityNotificationPolicy | MissingType
        ) = MISSING,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        :param body: The parameters to validate against the flow's input schema.
        :param label: A short human-readable title.
        :param tags: A collection of searchable tags associated with the run.
            Tags are normalized by stripping leading and trailing whitespace,
            and replacing all whitespace with a single space.
        :param run_monitors: A list of Globus Auth principals (identified by URN)
            authorized to monitor this run (in addition to the run owner).
        :param run_managers: A list of Globus Auth principals (identified by URN)
            authorized to manage this run (in addition to the run owner).
        :param activity_notification_policy:
            A policy document which declares when the Flows service will send
            notification emails regarding the run's activity.
        :param additional_fields: Additional key/value pairs sent to the run API.
            This parameter can be used to bypass SDK parameter validation.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import SpecificFlowClient

                    ...
                    flow = SpecificFlowClient(flow_id, ...)
                    flow.validate_run(body={"param": "value"})
            .. tab-item:: Example Response Data

                .. expandtestfixture:: flows.validate_run
        """

        data = {
            "body": body,
            "tags": tags,
            "label": label,
            "run_monitors": run_monitors,
            "run_managers": run_managers,
            "activity_notification_policy": activity_notification_policy,
        }
        data.update(additional_fields or {})

        return self.post(f"/flows/{self._flow_id}/validate_run", data=data)
