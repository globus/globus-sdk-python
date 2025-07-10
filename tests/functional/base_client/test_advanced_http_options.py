from globus_sdk.testing import RegisteredResponse, load_response


def test_allow_redirects_false(client):
    # based on a real response from 'GET https://auth.globus.org/'
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar",
            status=302,
            headers={
                "Date": "Fri, 15 Apr 2022 15:35:44 GMT",
                "Content-Type": "text/html",
                "Connection": "keep-alive",
                "Server": "nginx",
                "Location": "https://www.globus.org/",
            },
            body="""\
<html>
<head><title>302 Found</title></head>
<body>
<center><h1>302 Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
""",
        )
    )
    # NOTE: this test isn't very "real" because of where `responses` intercepts the
    # request/response action
    # even without `allow_redirects=False`, this test would pass
    # if we find a better way of testing redirect behavior, consider removing this test
    res = client.request("GET", "/bar", allow_redirects=False)
    assert res.http_status == 302


def test_stream_true(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar",
            json={"foo": "bar"},
        )
    )
    res = client.request("GET", "/bar", stream=True)
    assert res.http_status == 200
    # forcing JSON evaluation still works as expected (this must force the download /
    # evaluation of content)
    assert res["foo"] == "bar"
