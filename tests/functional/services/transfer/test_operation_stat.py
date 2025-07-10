"""
Tests for TransferClient.operation_stat
"""

import urllib.parse

from globus_sdk.testing import get_last_request, load_response


def test_operation_stat(client):
    meta = load_response(client.operation_stat).metadata
    endpoint_id = meta["endpoint_id"]
    path = "/home/share/godata/file1.txt"
    res = client.operation_stat(endpoint_id, path)

    assert res["name"] == "file1.txt"
    assert res["type"] == "file"
    assert res["size"] == 4

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"path": [path]}
