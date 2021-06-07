import json
import os
import uuid
from unittest import mock

import pytest

import globus_sdk
from globus_sdk.client import BaseClient
from tests.common import get_last_request, register_api_route


@pytest.fixture
def auth_client():
    return globus_sdk.NativeAppAuthClient(client_id=uuid.uuid1())


@pytest.fixture
def base_client(no_retry_policy):
    class CustomClient(BaseClient):
        base_path = "/v0.10/"
        service_name = "transfer"
        retry_policy = no_retry_policy

    return CustomClient()


# not particularly special, just a handy array of codes which should raise
# errors when encountered
ERROR_STATUS_CODES = (400, 404, 405, 409, 500, 503)


def test_cannot_instantiate_plain_base_client():
    # attempting to instantiate a BaseClient errors
    with pytest.raises(NotImplementedError):
        BaseClient()


def test_set_http_timeout(base_client):
    class FooClient(BaseClient):
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


def test_set_app_name(base_client):
    """
    Sets app name, confirms results
    """
    # set app name
    base_client.app_name = "SDK Test"
    # confirm results
    assert base_client.app_name == "SDK Test"
    assert (
        base_client.transport.user_agent
        == f"{base_client.transport.BASE_USER_AGENT}/SDK Test"
    )


def test_qjoin_path(base_client):
    """
    Calls qjoin on parts to form a path, confirms results
    """
    parts = ["SDK", "Test", "Path", "Items"]
    path = base_client.qjoin_path(*parts)
    assert path == "/SDK/Test/Path/Items"


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
    register_api_route(
        "transfer", "/madeuppath/objectname", method=methodname, json={"x": "y"}
    )

    # client should be able to compose the path itself
    path = base_client.qjoin_path("madeuppath", "objectname")

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
