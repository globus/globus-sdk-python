import logging
from typing import Any, Callable, Dict, Optional, TypeVar

from globus_sdk import client, scopes, utils

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
