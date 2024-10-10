from __future__ import annotations

import logging
import typing as t

from globus_sdk import GlobusHTTPResponse, client
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import ComputeScopes, Scope

from .data import ComputeFunctionDocument
from .errors import ComputeAPIError

log = logging.getLogger(__name__)


class ComputeClient(client.BaseClient):
    r"""
    Client for the Globus Compute API.

    .. automethodlist:: globus_sdk.ComputeClient
    """

    error_class = ComputeAPIError
    service_name = "compute"
    scopes = ComputeScopes
    default_scope_requirements = [Scope(ComputeScopes.all)]

    def register_function(
        self,
        function_data: ComputeFunctionDocument | dict[str, t.Any],
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
