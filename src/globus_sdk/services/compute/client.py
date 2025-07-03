from __future__ import annotations

import logging
import typing as t

from globus_sdk import MISSING, GlobusHTTPResponse, MissingType, client, utils
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import ComputeScopes, Scope

from .errors import ComputeAPIError

log = logging.getLogger(__name__)


class ComputeClientV2(client.BaseClient):
    r"""
    Client for the Globus Compute API, version 2.

    .. sdk-sphinx-copy-params:: BaseClient

    .. automethodlist:: globus_sdk.ComputeClientV2
    """

    error_class = ComputeAPIError
    service_name = "compute"
    scopes = ComputeScopes
    default_scope_requirements = [Scope(ComputeScopes.all)]

    def get_version(self, service: str | None = None) -> GlobusHTTPResponse:
        """Get the current version of the API and other services.

        :param service: Service for which to get version information.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Version
                    :service: compute
                    :ref: Root/operation/get_version_v2_version_get
        """
        query_params = {"service": service} if service else None
        return self.get("/v2/version", query_params=query_params)

    def get_result_amqp_url(self) -> GlobusHTTPResponse:
        """Generate new credentials (in the form of a connection URL) for
        connecting to the AMQP service.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Result AMQP URL
                    :service: compute
                    :ref: Root/operation/get_user_specific_result_amqp_url_v2_get_amqp_result_connection_url_get
        """  # noqa: E501
        return self.get("/v2/get_amqp_result_connection_url")

    def register_endpoint(self, data: dict[str, t.Any]) -> GlobusHTTPResponse:
        """Register a new endpoint.

        :param data: An endpoint registration document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Register Endpoint
                    :service: compute
                    :ref: Endpoints/operation/register_endpoint_v2_endpoints_post
        """
        return self.post("/v2/endpoints", data=data)

    def get_endpoint(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Get information about a registered endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Endpoint
                    :service: compute
                    :ref: Endpoints/operation/get_endpoint_v2_endpoints__endpoint_uuid__get
        """  # noqa: E501
        return self.get(f"/v2/endpoints/{endpoint_id}")

    def get_endpoint_status(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Get the status of a registered endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Endpoint Status
                    :service: compute
                    :ref: Endpoints/operation/get_endpoint_status_v2_endpoints__endpoint_uuid__status_get
        """  # noqa: E501
        return self.get(f"/v2/endpoints/{endpoint_id}/status")

    def get_endpoints(self, role: str | MissingType = MISSING) -> GlobusHTTPResponse:
        """Get a list of registered endpoints associated with the authenticated user.

        :param role: Role of the user in relation to endpoints. (e.g.: owner, any)

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Endpoints
                    :service: compute
                    :ref: Endpoints/operation/get_endpoints_v2_endpoints_get
        """  # noqa: E501
        query_params = {"role": role}
        return self.get("/v2/endpoints", query_params=query_params)

    def delete_endpoint(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Delete a registered endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Delete Endpoint
                    :service: compute
                    :ref: Endpoints/operation/delete_endpoint_v2_endpoints__endpoint_uuid__delete
        """  # noqa: E501
        return self.delete(f"/v2/endpoints/{endpoint_id}")

    def lock_endpoint(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Temporarily block registration requests for the endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Lock Endpoint
                    :service: compute
                    :ref: Endpoints/operation/lock_endpoint_v2_endpoints__endpoint_uuid__lock_post
        """  # noqa: E501
        return self.post(f"/v2/endpoints/{endpoint_id}/lock")

    def register_function(
        self,
        function_data: dict[str, t.Any],
    ) -> GlobusHTTPResponse:
        """Register a new function.

        :param function_data: A function registration document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Register Function
                    :service: compute
                    :ref: Functions/operation/register_function_v2_functions_post
        """  # noqa: E501
        return self.post("/v2/functions", data=function_data)

    def get_function(self, function_id: UUIDLike) -> GlobusHTTPResponse:
        """Get information about a registered function.

        :param function_id: The ID of the function.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Function
                    :service: compute
                    :ref: Functions/operation/get_function_v2_functions__function_uuid__get
        """  # noqa: E501
        return self.get(f"/v2/functions/{function_id}")

    def delete_function(self, function_id: UUIDLike) -> GlobusHTTPResponse:
        """Delete a registered function.

        :param function_id: The ID of the function.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Delete Function
                    :service: compute
                    :ref: Functions/operation/delete_function_v2_functions__function_uuid__delete
        """  # noqa: E501
        return self.delete(f"/v2/functions/{function_id}")

    def get_task(self, task_id: UUIDLike) -> GlobusHTTPResponse:
        """Get information about a task.

        :param task_id: The ID of the task.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Task
                    :service: compute
                    :ref: Tasks/operation/get_task_status_and_result_v2_tasks__task_uuid__get
        """  # noqa: E501
        return self.get(f"/v2/tasks/{task_id}")

    def get_task_batch(
        self, task_ids: UUIDLike | t.Iterable[UUIDLike]
    ) -> GlobusHTTPResponse:
        """Get information about a batch of tasks.

        :param task_ids: The IDs of the tasks.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Task Batch
                    :service: compute
                    :ref: Root/operation/get_batch_status_v2_batch_status_post
        """
        task_ids = list(utils.safe_strseq_iter(task_ids))
        return self.post("/v2/batch_status", data={"task_ids": task_ids})

    def get_task_group(self, task_group_id: UUIDLike) -> GlobusHTTPResponse:
        """Get a list of task IDs associated with a task group.

        :param task_group_id: The ID of the task group.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Task Group Tasks
                    :service: compute
                    :ref: TaskGroup/operation/get_task_group_tasks_v2_taskgroup__task_group_uuid__get
        """  # noqa: E501
        return self.get(f"/v2/taskgroup/{task_group_id}")

    def submit(self, data: dict[str, t.Any]) -> GlobusHTTPResponse:
        """Submit a batch of tasks to a Globus Compute endpoint.

        :param data: The task batch document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Submit Batch
                    :service: compute
                    :ref: Root/operation/submit_batch_v2_submit_post
        """  # noqa: E501
        return self.post("/v2/submit", data=data)


class ComputeClientV3(client.BaseClient):
    r"""
    Client for the Globus Compute API, version 3.

    .. automethodlist:: globus_sdk.ComputeClientV3
    """

    error_class = ComputeAPIError
    service_name = "compute"
    scopes = ComputeScopes
    default_scope_requirements = [Scope(ComputeScopes.all)]

    def register_endpoint(self, data: dict[str, t.Any]) -> GlobusHTTPResponse:
        """Register a new endpoint.

        :param data: An endpoint registration document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Register Endpoint
                    :service: compute
                    :ref: Endpoints/operation/register_endpoint_v3_endpoints_post
        """
        return self.post("/v3/endpoints", data=data)

    def update_endpoint(
        self, endpoint_id: UUIDLike, data: dict[str, t.Any]
    ) -> GlobusHTTPResponse:
        """Update an endpoint.

        :param endpoint_id: The ID of the endpoint.
        :param data: An endpoint update document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Update Endpoint
                    :service: compute
                    :ref: Endpoints/operation/update_endpoint_v3_endpoints__endpoint_uuid__put
        """  # noqa: E501
        return self.put(f"/v3/endpoints/{endpoint_id}", data=data)

    def lock_endpoint(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Temporarily block registration requests for the endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Lock Endpoint
                    :service: compute
                    :ref: Endpoints/operation/lock_endpoint_v3_endpoints__endpoint_uuid__lock_post
        """  # noqa: E501
        return self.post(f"/v3/endpoints/{endpoint_id}/lock")

    def get_endpoint_allowlist(self, endpoint_id: UUIDLike) -> GlobusHTTPResponse:
        """Get a list of IDs for functions allowed to run on an endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Get Endpoint Allowlist
                    :service: compute
                    :ref: Endpoints/operation/get_endpoint_allowlist_v3_endpoints__endpoint_uuid__allowed_functions_get
        """  # noqa: E501
        return self.get(f"/v3/endpoints/{endpoint_id}/allowed_functions")

    def register_function(self, data: dict[str, t.Any]) -> GlobusHTTPResponse:
        """Register a new function.

        :param data: A function registration document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Register Function
                    :service: compute
                    :ref: Functions/operation/register_function_v3_functions_post
        """
        return self.post("/v3/functions", data=data)

    def submit(
        self, endpoint_id: UUIDLike, data: dict[str, t.Any]
    ) -> GlobusHTTPResponse:
        """Submit a batch of tasks to a Globus Compute endpoint.

        :param endpoint_id: The ID of the Globus Compute endpoint.
        :param data: The task batch document.

        .. tab-set::

            .. tab-item:: API Info

                .. extdoclink:: Submit Batch
                    :service: compute
                    :ref: Endpoints/operation/submit_batch_v3_endpoints__endpoint_uuid__submit_post
        """  # noqa: E501
        return self.post(f"/v3/endpoints/{endpoint_id}/submit", data=data)


class ComputeClient(ComputeClientV2):
    r"""
    Canonical client for the Globus Compute API, with support exclusively for
    API version 2.

    .. sdk-sphinx-copy-params:: BaseClient
    """
