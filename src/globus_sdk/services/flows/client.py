import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar

from globus_sdk import GlobusHTTPResponse, client, scopes, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.scopes import ScopeBuilder

from .errors import FlowsAPIError
from .response import IterableFlowsResponse

log = logging.getLogger(__name__)

C = TypeVar("C", bound=Callable[..., Any])


def _flowdoc(message: str, link: str) -> Callable[[C], C]:
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

    @_flowdoc("List Flows", "Flows/paths/~1flows/get")
    def list_flows(
        self,
        *,
        filter_role: Optional[str] = None,
        filter_fulltext: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableFlowsResponse:
        """List deployed Flows

        :param filter_role: A role name specifying the minimum permissions required for
            a Flow to be included in the response.
        :type filter_role: str, optional
        :param filter_fulltext: A string to use in a full-text search to filter results
        :type filter_fulltext: str, optional
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
        """

        if query_params is None:
            query_params = {}
        if filter_role is not None:
            query_params["filter_role"] = filter_role
        if filter_fulltext is not None:
            query_params["filter_fulltext"] = filter_fulltext

        return IterableFlowsResponse(self.get("/flows", query_params=query_params))


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
        environment: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
        app_name: Optional[str] = None,
        transport_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            environment=environment,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )
        self._flow_id = flow_id
        self.scopes = ScopeBuilder(
            resource_server=str(self._flow_id),
            known_url_scopes=[f"flow_{flow_id}_user"],
        )

    @_flowdoc("Run Flow", "~1flows~1{flow_id}~1run/post")
    def run_flow(
        self,
        body: Dict[str, Any],
        *,
        label: Optional[str] = None,
        tags: Optional[List[str]] = None,
        run_monitors: Optional[List[str]] = None,
        run_managers: Optional[List[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
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
