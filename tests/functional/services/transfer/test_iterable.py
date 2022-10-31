"""
Tests for IterableTransferResponse responses from TransferClient
"""
import globus_sdk
from tests.common import register_api_route

SERVER_LIST_TEXT = """{
  "DATA": [
    {
      "DATA_TYPE": "server",
      "hostname": "ep1.transfer.globus.org",
      "id": 207976,
      "incoming_data_port_end": null,
      "incoming_data_port_start": null,
      "is_connected": true,
      "is_paused": false,
      "outgoing_data_port_end": null,
      "outgoing_data_port_start": null,
      "port": 2811,
      "scheme": "gsiftp",
      "subject": null,
      "uri": "gsiftp://ep1.transfer.globus.org:2811"
    }
  ],
  "DATA_TYPE": "endpoint_server_list",
  "endpoint": "go#ep1"
}"""


def test_server_list(client):
    epid = "epid"
    register_api_route(
        "transfer", f"/endpoint/{epid}/server_list", body=SERVER_LIST_TEXT
    )

    res = client.endpoint_server_list(epid)
    # it should still be a subclass of GlobusHTTPResponse
    assert isinstance(res, globus_sdk.GlobusHTTPResponse)

    # fetch top-level attrs
    assert res["DATA_TYPE"] == "endpoint_server_list"
    assert res["endpoint"] == "go#ep1"

    # intentionally access twice -- unlike PaginatedResource, this is allowed
    # and works
    assert len(list(res)) == 1
    assert len(list(res)) == 1

    assert list(res)[0]["DATA_TYPE"] == "server"
