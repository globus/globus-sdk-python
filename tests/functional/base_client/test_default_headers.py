from globus_sdk import __version__
from globus_sdk._testing import RegisteredResponse, get_last_request


def test_clientinfo_header_default(client):
    RegisteredResponse(
        path="https://foo.api.globus.org/bar",
        json={"foo": "bar"},
    ).add()
    res = client.request("GET", "/bar")
    assert res.http_status == 200

    req = get_last_request()
    assert "X-Globus-Client-Info" in req.headers
    assert (
        req.headers["X-Globus-Client-Info"]
        == f"product=python-sdk,version={__version__}"
    )


def test_clientinfo_header_can_be_supressed(client):
    RegisteredResponse(
        path="https://foo.api.globus.org/bar",
        json={"foo": "bar"},
    ).add()

    # clear the X-Globus-Client-Info header
    client.transport.globus_client_info.clear()

    res = client.request("GET", "/bar")
    assert res.http_status == 200

    req = get_last_request()
    assert "X-Globus-Client-Info" not in req.headers
