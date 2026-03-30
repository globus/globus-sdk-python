from globus_sdk.testing import get_last_request, load_response


def test_list_stream_access_points(client):
    meta = load_response(client.list_stream_access_points).metadata

    res = client.list_stream_access_points()
    assert res.http_status == 200
    list_results = list(res)

    assert len(list_results) == 2
    for stream_access_point in list_results:
        assert stream_access_point["type"] == "StreamAccessPoint"
        assert stream_access_point["id"] in meta["access_point_ids"]

    req = get_last_request()
    assert req.body is None
