import json
import os
import uuid
from unittest import mock

import pytest

import globus_sdk
import globus_sdk.scopes
from tests.common import get_last_request, register_api_route


@pytest.fixture
def auth_client():
    return globus_sdk.NativeAppAuthClient(client_id=uuid.uuid1())


@pytest.fixture
def base_client_class(no_retry_transport):
    class CustomClient(globus_sdk.BaseClient):
        base_path = "/v0.10/"
        service_name = "transfer"
        transport_class = no_retry_transport
        scopes = globus_sdk.scopes.TransferScopes

    return CustomClient


@pytest.fixture
def base_client(base_client_class):
    return base_client_class()


# not particularly special, just a handy array of codes which should raise
# errors when encountered
ERROR_STATUS_CODES = (400, 404, 405, 409, 500, 503)


def test_cannot_instantiate_plain_base_client():
    # attempting to instantiate a BaseClient errors
    with pytest.raises(NotImplementedError):
        globus_sdk.BaseClient()


def test_set_http_timeout(base_client):
    class FooClient(globus_sdk.BaseClient):
        service_name = "foo"

    with mock.patch.dict(os.environ):
        # ensure not set
        os.environ.pop("GLOBUS_SDK_HTTP_TIMEOUT", None)

        client = FooClient()
        assert client.transport.http_timeout == 60.0

        client = FooClient(transport_params={"http_timeout": None})
        assert client.transport.http_timeout == 60.0

        client = FooClient(transport_params={"http_timeout": -1})
        assert client.transport.http_timeout is None

        os.environ["GLOBUS_SDK_HTTP_TIMEOUT"] = "120"
        client = FooClient()
        assert client.transport.http_timeout == 120.0

        os.environ["GLOBUS_SDK_HTTP_TIMEOUT"] = "-1"
        client = FooClient()
        assert client.transport.http_timeout is None


@pytest.mark.parametrize("mode", ("init", "post_init"))
def test_set_app_name(base_client, base_client_class, mode):
    """
    Sets app name, confirms results
    """
    # set app name
    if mode == "post_init":
        c = base_client
        base_client.app_name = "SDK Test"
    elif mode == "init":
        c = base_client_class(app_name="SDK Test")
    else:
        raise NotImplementedError

    # confirm results
    assert c.app_name == "SDK Test"
    assert c.transport.user_agent == f"{c.transport.BASE_USER_AGENT}/SDK Test"


@pytest.mark.parametrize(
    "method, allows_body",
    [("get", False), ("delete", False), ("post", True), ("put", True), ("patch", True)],
)
def test_http_methods(method, allows_body, base_client):
    """
    BaseClient.{get, delete, post, put, patch} on a path does "the right thing"
    Sends a text body or JSON body as requested
    Raises a GlobusAPIError if the response is not a 200

    NOTE: tests sending request bodies even on GET (which
    *shouldn't* have bodies but *may* have them in reality).
    """
    methodname = method.upper()
    resolved_method = getattr(base_client, method)
    path = "/madeuppath/objectname"
    register_api_route("transfer", path, method=methodname, json={"x": "y"})

    # request with no body
    res = resolved_method(path)
    req = get_last_request()

    assert req.method == methodname
    assert req.body is None
    assert "x" in res
    assert res["x"] == "y"

    if allows_body:
        jsonbody = {"foo": "bar"}
        res = resolved_method(path, data=jsonbody)
        req = get_last_request()

        assert req.method == methodname
        assert req.body == json.dumps(jsonbody).encode("utf-8")
        assert "x" in res
        assert res["x"] == "y"

        res = resolved_method(path, data="abc")
        req = get_last_request()

        assert req.method == methodname
        assert req.body == "abc"
        assert "x" in res
        assert res["x"] == "y"

    # send "bad" request
    for status in ERROR_STATUS_CODES:
        register_api_route(
            "transfer",
            "/madeuppath/objectname",
            method=methodname,
            status=status,
            json={"x": "y", "code": "ErrorCode", "message": "foo"},
            replace=True,
        )

        with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
            resolved_method("/madeuppath/objectname")

        assert excinfo.value.http_status == status
        assert excinfo.value.raw_json["x"] == "y"
        assert excinfo.value.code == "ErrorCode"
        assert excinfo.value.message == "foo"


def test_handle_url_unsafe_chars(base_client):
    # make sure this path (escaped) and the request path (unescaped) match
    register_api_route("transfer", "/foo/foo%20bar", json={"x": "y"})
    res = base_client.get("foo/foo bar")
    assert "x" in res
    assert res["x"] == "y"


def test_access_resource_server_property_via_instance(base_client):
    # get works (and returns accurate info)
    assert (
        base_client.resource_server == globus_sdk.scopes.TransferScopes.resource_server
    )


def test_access_resource_server_property_via_class(base_client_class):
    # get works (and returns accurate info)
    assert (
        base_client_class.resource_server
        == globus_sdk.scopes.TransferScopes.resource_server
    )
