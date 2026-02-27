from __future__ import annotations

import logging
import typing as t
import uuid

from globus_sdk import client, exc, paging, response
from globus_sdk._missing import MISSING
from globus_sdk.response import IterableJSONAPIResponse
from globus_sdk.scopes import TransferScopes
from globus_sdk.services.transfer.errors import TransferAPIError
from globus_sdk.transport import RetryConfig

from .data import CreateTunnelData
from .transport import TRANSFER_V2_DEFAULT_RETRY_CHECKS

log = logging.getLogger(__name__)


class TransferClientV2(client.BaseClient):
    r"""
    Client for the `/v2/ routes of the Globus Transfer API
    <https://docs.globus.org/api/transfer/#v2>`_.

    .. sdk-sphinx-copy-params:: BaseClient

    This class provides helper methods for /v2/ functionality in the Transfer
    API as it is developed.

    **Paginated Calls**

    Methods which support pagination can be called as paginated or unpaginated methods.
    If the method name is ``TransferClientV2.foo``, the paginated version is
    ``TransferClientV2.paginated.foo``.
    Using ``TransferClientV2.list_stream_access_points`` as an example::

        from globus_sdk.experimental.transfer_v2 import TransferClientV2
        tc = TransferClientV2(...)

        # this is the unpaginated version
        for stream_access_point in tc.list_stream_access_points():
            print(stream_access_point["attributes"]["display_name"])

        # this is the paginated version
        for page in tc.paginated.list_stream_access_points():
            for stream_access_point in page:
                print(stream_access_point["attributes"]["display_name"])

    .. automethodlist:: globus_sdk.TransferClient
    """

    service_name = "transfer"
    error_class = TransferAPIError
    scopes = TransferScopes
    default_scope_requirements = [TransferScopes.all]

    def _register_standard_retry_checks(self, retry_config: RetryConfig) -> None:
        """Override the default retry checks."""
        retry_config.checks.register_many_checks(TRANSFER_V2_DEFAULT_RETRY_CHECKS)

    # Tunnel methods

    def create_tunnel(
        self,
        data: dict[str, t.Any] | CreateTunnelData,
    ) -> response.GlobusHTTPResponse:
        """
        :param data: Parameters for the tunnel creation

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    result = tc.create_tunnel(data)
                    print(result["data"]["id"])

            .. tab-item:: API Info

                ``POST /v2/tunnels``
        """
        log.debug("TransferClientV2.create_tunnel(...)")
        try:
            data_element = data["data"]
        except KeyError as e:
            raise exc.GlobusSDKUsageError(
                "create_tunnel() body was malformed (missing the 'data' key). "
                "Use CreateTunnelData to easily create correct documents."
            ) from e

        try:
            attributes = data_element["attributes"]
        except KeyError:
            data_element["attributes"] = {}
            attributes = data_element["attributes"]
        if attributes.get("submission_id", MISSING) is MISSING:
            log.debug("create_tunnel auto-creating submission_id")
            attributes["submission_id"] = str(uuid.uuid1())

        r = self.post("/v2/tunnels", data=data)
        return r

    def update_tunnel(
        self,
        tunnel_id: str | uuid.UUID,
        update_doc: dict[str, t.Any],
    ) -> response.GlobusHTTPResponse:
        r"""
        :param tunnel_id: The ID of the Tunnel.
        :param update_doc: The document that will be sent to the patch API.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    "data" = {
                        "type": "Tunnel",
                        "attributes": {
                            "state": "STOPPING",
                        },
                    }
                    result = tc.update_tunnel(tunnel_id, data)
                    print(result["data"])

            .. tab-item:: API Info

                ``PATCH /v2/tunnels/<tunnel_id>``
        """
        log.debug(f"TransferClientV2.update_tunnel({tunnel_id}, {update_doc})")
        r = self.patch(f"/v2/tunnels/{tunnel_id}", data=update_doc)
        return r

    def get_tunnel(
        self,
        tunnel_id: str | uuid.UUID,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param tunnel_id: The ID of the Tunnel which we are fetching details about.
        :param query_params: Any additional parameters will be passed through
            as query params.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    result = tc.show_tunnel(tunnel_id)
                    print(result["data"])

            .. tab-item:: API Info

                ``GET /v2/tunnels/<tunnel_id>``
        """
        log.debug("TransferClientV2.get_tunnel({tunnel_id}, {query_params})")
        r = self.get(f"/v2/tunnels/{tunnel_id}", query_params=query_params)
        return r

    def delete_tunnel(
        self,
        tunnel_id: str | uuid.UUID,
    ) -> response.GlobusHTTPResponse:
        """
        :param tunnel_id: The ID of the Tunnel to be deleted.

        This will clean up all data associated with a Tunnel.
        Note that Tunnels must be stopped before they can be deleted.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    tc.delete_tunnel(tunnel_id)

            .. tab-item:: API Info

                ``DELETE /v2/tunnels/<tunnel_id>``
        """
        log.debug(f"TransferClientV2.delete_tunnel({tunnel_id})")
        r = self.delete(f"/v2/tunnels/{tunnel_id}")
        return r

    def list_tunnels(
        self,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableJSONAPIResponse:
        """
        :param query_params: Any additional parameters will be passed through
            as query params.

        This will list all the Tunnels created by the authorized user.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    tc.list_tunnels(tunnel_id)

            .. tab-item:: API Info

                ``GET /v2/tunnels/``
        """
        log.debug(f"TransferClientV2.list_tunnels({query_params})")
        r = self.get("/v2/tunnels", query_params=query_params)
        return IterableJSONAPIResponse(r)

    def get_tunnel_events(
        self,
        tunnel_id: str | uuid.UUID,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableJSONAPIResponse:
        """
        :param tunnel_id: The ID of the Tunnel which we are fetching events about.
        :param query_params: Any additional parameters will be passed through
            as query params.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    result = tc.get_tunnel_events(tunnel_id)
                    print(result["data"])

            .. tab-item:: API Info

                ``GET /v2/tunnels/<tunnel_id>/events``
        """
        log.debug(f"TransferClientV2.get_tunnel_events({tunnel_id}, {query_params})")
        r = self.get(f"/v2/tunnels/{tunnel_id}/events", query_params=query_params)
        return IterableJSONAPIResponse(r)

    # Stream access point methods

    def get_stream_access_point(
        self,
        stream_ap_id: str | uuid.UUID,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        :param stream_ap_id: The ID of the steaming access point to lookup.
        :param query_params: Any additional parameters will be passed through
            as query params.

        Get a stream access point by id.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    tc.get_stream_access_point(stream_ap_id)

            .. tab-item:: API Info

                ``GET /v2/stream_access_points/<stream_ap_id>``
        """
        log.debug(
            f"TransferClientV2.get_stream_access_point({stream_ap_id}, {query_params})"
        )
        r = self.get(
            f"/v2/stream_access_points/{stream_ap_id}", query_params=query_params
        )
        return r

    @paging.has_paginator(paging.JSONAPIPaginator)
    def list_stream_access_points(
        self,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> IterableJSONAPIResponse:
        """
        :param query_params: Any additional parameters will be passed through
            as query params.

        List stream access points.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    tc = globus_sdk.TrasferClientV2(...)
                    tc.list_stream_access_points()

            .. tab-item:: API Info

                ``GET /v2/stream_access_points``
        """
        log.debug(f"TransferClientV2.list_stream_access_points({query_params})")
        r = self.get("/v2/stream_access_points", query_params=query_params)
        return IterableJSONAPIResponse(r)
