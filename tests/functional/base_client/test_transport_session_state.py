"""
The transport owns a ``requests.Session``, but it sends requests with
``session.send(request.prepare())`` and never calls ``Session.prepare_request``.
The SDK therefore does not use the session's headers, params, auth, hooks, or cookies:
the transport and the client configure those things themselves.

These tests pin that behavior down, for requests which are sent directly
and for requests which are redirected.
"""

import pytest
import responses

import globus_sdk
from globus_sdk.testing import get_last_request

BASE_URL = "https://foo.api.globus.org"
OTHER_URL = "https://other.api.globus.org"


def _add_redirect(from_url, to_url):
    responses.add(
        responses.GET,
        from_url,
        status=302,
        headers={"Location": to_url},
    )


def _send(client, *, redirected):
    """
    Send one GET and return the last request which went over the (mocked) wire.

    If ``redirected`` is True, the request is redirected once,
    and the returned request is the redirect hop, not the first hop.
    """

    if redirected:
        _add_redirect(f"{BASE_URL}/start", f"{BASE_URL}/end")
        responses.add(responses.GET, f"{BASE_URL}/end", json={})
        client.get("/start")
    else:
        responses.add(responses.GET, f"{BASE_URL}/end", json={})
        client.get("/end")

    req = get_last_request()
    assert req.url.startswith(f"{BASE_URL}/end")
    return req


# --- cookies ---


def test_cookie_from_earlier_response_is_not_sent_on_a_direct_request(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/set-cookie",
        json={},
        headers={"Set-Cookie": "session=SECRET; Path=/"},
    )
    client.get("/set-cookie")

    req = _send(client, redirected=False)
    assert "Cookie" not in req.headers


@pytest.mark.parametrize(
    "redirect_origin",
    (
        pytest.param("same-host", id="redirect-within-the-cookie-host"),
        pytest.param("other-host", id="redirect-from-another-host"),
    ),
)
def test_cookie_from_earlier_response_is_not_sent_on_a_redirect_hop(
    client, client_class, redirect_origin
):
    # one response sets a cookie
    responses.add(
        responses.GET,
        f"{BASE_URL}/set-cookie",
        json={},
        headers={"Set-Cookie": "session=SECRET; Path=/"},
    )
    client.get("/set-cookie")

    # a later, unrelated request is redirected to a URL the cookie matches
    if redirect_origin == "same-host":
        second_client = client
        second_url = f"{BASE_URL}/start"
    else:
        # a different client with a different base URL, sharing one transport
        second_client = client_class(base_url=OTHER_URL, transport=client.transport)
        second_url = f"{OTHER_URL}/start"
    _add_redirect(second_url, f"{BASE_URL}/end")
    responses.add(responses.GET, f"{BASE_URL}/end", json={})

    second_client.get("/start")

    req = get_last_request()
    assert req.url == f"{BASE_URL}/end"
    assert "Cookie" not in req.headers


def test_cookie_from_a_failed_attempt_is_not_sent_on_a_redirect_hop_of_the_retry(
    client,
):
    # The cookie is stored by the first attempt's 503 (e.g., a load balancer's
    # sticky-session cookie). The retry is a first hop, so it does not carry the
    # cookie, but if the retry is redirected, that hop does.
    responses.add(
        responses.GET,
        f"{BASE_URL}/flaky",
        status=503,
        headers={"Set-Cookie": "sticky=NODE-A; Path=/"},
    )
    _add_redirect(f"{BASE_URL}/flaky", f"{BASE_URL}/end")
    responses.add(responses.GET, f"{BASE_URL}/end", json={})

    client.get("/flaky")

    # guard against this test silently ceasing to test a retry followed by a redirect
    assert [call.response.status_code for call in responses.calls] == [503, 302, 200]
    req = get_last_request()
    assert req.url == f"{BASE_URL}/end"
    assert "Cookie" not in req.headers


# --- other session state which is not used ---


@pytest.mark.parametrize("redirected", (False, True), ids=("direct", "redirected"))
def test_session_headers_are_not_sent(client, redirected):
    client.transport.session.headers["X-Session-Header"] = "from-the-session"

    req = _send(client, redirected=redirected)

    assert "X-Session-Header" not in req.headers
    # the SDK's own identification is used, not the session's
    assert req.headers["User-Agent"] == client.transport.user_agent
    assert "python-requests" not in req.headers["User-Agent"]


def test_session_params_are_not_sent(client):
    # not parametrized over redirects: a redirect hop's URL comes from `Location`
    client.transport.session.params = {"from_session": "1"}

    req = _send(client, redirected=False)

    assert "from_session" not in req.url


@pytest.mark.parametrize("redirected", (False, True), ids=("direct", "redirected"))
def test_session_auth_is_not_sent(client, redirected):
    client.transport.session.auth = ("session-user", "session-password")

    req = _send(client, redirected=redirected)

    assert "Authorization" not in req.headers


@pytest.mark.parametrize("redirected", (False, True), ids=("direct", "redirected"))
def test_session_hooks_are_not_run(client, redirected):
    calls = []

    def hook(response, **kwargs):
        calls.append(response.url)
        return response

    client.transport.session.hooks["response"].append(hook)

    _send(client, redirected=redirected)

    assert calls == []


def test_authorizer_provides_authorization_despite_session_auth(client_class):
    # the only source of an Authorization header is the client's authorizer
    client = client_class(authorizer=globus_sdk.AccessTokenAuthorizer("sdk-token"))
    client.transport.session.auth = ("session-user", "session-password")

    req = _send(client, redirected=False)

    assert req.headers["Authorization"] == "Bearer sdk-token"
