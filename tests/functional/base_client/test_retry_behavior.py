import pytest
import requests

import globus_sdk
from globus_sdk.testing import RegisteredResponse, load_response
from globus_sdk.transport import RequestCallerInfo


@pytest.mark.parametrize("error_status", [500, 429, 502, 503, 504])
def test_retry_on_transient_error(client, mocksleep, error_status):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=error_status, body="Uh-oh!"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # there was a sleep (retry was triggered)
    mocksleep.assert_called_once()


def test_retry_disabled_via_tune(client, mocksleep):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=500, body="Uh-oh!"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # the error is seen by the client (automatic retry does not hide it)
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        with client.transport.tune(max_retries=0):
            client.get("/bar")
    assert excinfo.value.http_status == 500

    # there was a no sleep (retry was not triggered)
    mocksleep.assert_not_called()


def test_retry_on_network_error(client, mocksleep):
    # set the response to be a requests NetworkError -- responses will raise the
    # exception when the call is made
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar",
            body=requests.ConnectionError("foo-err"),
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # there was a sleep (retry was triggered)
    mocksleep.assert_called_once()


@pytest.mark.parametrize("num_errors,expect_err", [(5, False), (6, True), (7, True)])
def test_retry_limit(client, mocksleep, num_errors, expect_err):
    # N errors followed by a success
    for _i in range(num_errors):
        load_response(
            RegisteredResponse(
                path="https://foo.api.globus.org/bar", status=500, body="Uh-oh!"
            )
        )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    if expect_err:
        with pytest.raises(globus_sdk.GlobusAPIError):
            client.get("/bar")
    else:
        # no sign of an error in the client
        res = client.get("/bar")
        assert res.http_status == 200
        assert res["baz"] == 1

    # default num retries = 5
    assert mocksleep.call_count == min(num_errors, 5)


def test_transport_retry_limit(client, mocksleep):
    # this limit is a safety to protect against a bad policy causing infinite retries
    client.transport.max_retries = 2

    for _i in range(3):
        load_response(
            RegisteredResponse(
                path="https://foo.api.globus.org/bar", status=500, body="Uh-oh!"
            )
        )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    with pytest.raises(globus_sdk.GlobusAPIError):
        client.get("/bar")

    assert mocksleep.call_count == 2


def test_bad_max_retries_causes_error(client):
    # this test exploits the fact that we loop to (transport.max_retries + 1) in order
    # to ensure that no requests are ever sent
    # the transport should throw an error in this case, since it doesn't have a response
    # value to return
    client.transport.max_retries = -1

    with pytest.raises(ValueError):
        client.get("/bar")


def test_persistent_connection_error(client):
    for _i in range(6):
        load_response(
            RegisteredResponse(
                path="https://foo.api.globus.org/bar",
                body=requests.ConnectionError("foo-err"),
            )
        )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    with pytest.raises(globus_sdk.GlobusConnectionError):
        client.get("/bar")


def test_no_retry_401_no_authorizer(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # error gets raised in client (no retry)
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401


def test_retry_with_authorizer(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # an authorizer class which does nothing but claims to support handling of
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def get_authorization_header(self):
            dummy_authz_calls.append("set_authz")
            return "foo"

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return True

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # no sign of an error in the client
    res = client.get("/bar")
    assert res.http_status == 200
    assert res["baz"] == 1

    # ensure that setting authz was called twice (once for each request)
    # and that between the two calls, handle_missing_authorization was called once
    assert dummy_authz_calls == ["set_authz", "handle_missing", "set_authz"]


def test_no_retry_with_authorizer_no_handler(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # an authorizer class which does nothing and does not claim to handle
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def get_authorization_header(self):
            dummy_authz_calls.append("set_authz")
            return "foo"

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return False

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # error gets raised in client (no retry)
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401

    # only two calls, single setting of authz and a call to ask about handling the error
    assert dummy_authz_calls == ["set_authz", "handle_missing"]


def test_retry_with_authorizer_persistent_401(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    # an authorizer class which does nothing but claims to support handling of
    # unauthorized errors
    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def get_authorization_header(self):
            dummy_authz_calls.append("set_authz")
            return "foo"

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return True

    authorizer = DummyAuthorizer()
    client.authorizer = authorizer

    # the error gets raised in this case because it persists -- the authorizer only gets
    # one chance to resolve the issue
    with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
        client.get("/bar")
    assert excinfo.value.http_status == 401

    # ensure that setting authz was called twice (once for each request)
    # and that between the two calls, handle_missing_authorization was called once
    # but the handler should not be called a second time because the 401 repeated
    assert dummy_authz_calls == ["set_authz", "handle_missing", "set_authz"]


def test_transport_caller_info_with_retry(client):
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar", status=401, body="Unauthorized"
        )
    )
    load_response(
        RegisteredResponse(path="https://foo.api.globus.org/bar", json={"baz": 1})
    )

    dummy_authz_calls = []

    class DummyAuthorizer(globus_sdk.authorizers.GlobusAuthorizer):
        def get_authorization_header(self):
            dummy_authz_calls.append("set_authz")
            return "foo"

        def handle_missing_authorization(self):
            dummy_authz_calls.append("handle_missing")
            return True

    authorizer = DummyAuthorizer()
    caller_info = RequestCallerInfo(
        retry_checks=client.request_retry_checks, authorizer=authorizer
    )

    # Test direct transport usage with caller_info
    response = client.transport.request(
        "GET", "https://foo.api.globus.org/bar", caller_info=caller_info
    )

    assert response.status_code == 200
    # Verify that the authorizer was used for both authorization and retry handling
    assert dummy_authz_calls == ["set_authz", "handle_missing", "set_authz"]
