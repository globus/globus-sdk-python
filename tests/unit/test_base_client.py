import json
import os
import uuid
from unittest import mock

import pytest

import globus_sdk
from globus_sdk import GlobusApp, GlobusAppConfig, GlobusSDKUsageError, UserApp
from globus_sdk._testing import RegisteredResponse, get_last_request
from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.scopes import Scope, TransferScopes
from globus_sdk.tokenstorage import TokenValidationError


@pytest.fixture
def auth_client():
    return globus_sdk.NativeAppAuthClient(client_id=uuid.uuid1())


@pytest.fixture
def base_client_class(no_retry_transport):
    class CustomClient(globus_sdk.BaseClient):
        service_name = "transfer"
        transport_class = no_retry_transport
        scopes = TransferScopes
        default_scope_requirements = [Scope(TransferScopes.all)]

    return CustomClient


@pytest.fixture
def base_client(base_client_class):
    return base_client_class()


# not particularly special, just a handy array of codes which should raise
# errors when encountered
ERROR_STATUS_CODES = (400, 404, 405, 409, 500, 503)


def test_cannot_instantiate_plain_base_client():
    # attempting to instantiate a BaseClient errors
    with pytest.raises(GlobusSDKUsageError):
        globus_sdk.BaseClient()


def test_can_instantiate_base_client_with_explicit_url():
    client = globus_sdk.BaseClient(base_url="https://example.org")
    assert client.base_url == "https://example.org"


def test_can_instantiate_with_base_url_class_attribute():
    class MyCoolClient(globus_sdk.BaseClient):
        base_url = "https://example.org/"

    client = MyCoolClient()
    assert client.base_url == "https://example.org/"


def test_base_url_resolution_precedence():
    """
    Base URL can come from one of 3 different places; this test asserts that we maintain
    a consistent precedence between the three
        (init-base_url > class-base_url > class-service_name)
    """

    class BothAttributesClient(globus_sdk.BaseClient):
        base_url = "class-base"
        service_name = "service-name"

    class OnlyServiceClient(globus_sdk.BaseClient):
        service_name = "service-name"

    # All 3 are set
    assert BothAttributesClient(base_url="init-base").base_url == "init-base"
    assert BothAttributesClient().base_url == "class-base"
    assert OnlyServiceClient().base_url == "https://service-name.api.globus.org/"


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
    path = "/v0.10/madeuppath/objectname"
    RegisteredResponse(
        service="transfer", path=path, method=methodname, json={"x": "y"}
    ).add()

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
        RegisteredResponse(
            service="transfer",
            path=path,
            method=methodname,
            json={"x": "y", "code": "ErrorCode", "message": "foo"},
            status=status,
        ).replace()

        with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
            resolved_method(path)

        assert excinfo.value.http_status == status
        assert excinfo.value.raw_json["x"] == "y"
        assert excinfo.value.code == "ErrorCode"
        assert excinfo.value.message == "foo"


def test_handle_url_unsafe_chars(base_client):
    # make sure this path (escaped) and the request path (unescaped) match
    RegisteredResponse(
        service="transfer", path="/v0.10/foo/foo%20bar", json={"x": "y"}
    ).add()
    res = base_client.get("/v0.10/foo/foo bar")
    assert "x" in res
    assert res["x"] == "y"


def test_access_resource_server_property_via_instance(base_client):
    # get works (and returns accurate info)
    assert base_client.resource_server == TransferScopes.resource_server


def test_access_resource_server_property_via_class(base_client_class):
    # get works (and returns accurate info)
    assert base_client_class.resource_server == TransferScopes.resource_server


def test_app_integration(base_client_class):
    def _reraise_token_error(_: GlobusApp, error: TokenValidationError):
        raise error

    config = GlobusAppConfig(token_validation_error_handler=_reraise_token_error)
    app = UserApp("SDK Test", client_id="client_id", config=config)

    c = base_client_class(app=app)

    # confirm app_name set
    assert c.app_name == "SDK Test"

    # confirm default_required_scopes were automatically added
    assert [str(s) for s in app.scope_requirements[c.resource_server]] == [
        TransferScopes.all
    ]

    # confirm attempt at getting an authorizer from app
    RegisteredResponse(
        service="transfer", path="foo", method="get", json={"x": "y"}
    ).add()
    with pytest.raises(TokenValidationError) as ex:
        c.get("foo")
    assert str(ex.value) == "No token data for transfer.api.globus.org"


def test_app_scopes(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    c = base_client_class(app=app, app_scopes=[Scope("foo")])

    # confirm app_scopes were added and default_required_scopes were not
    assert [str(s) for s in app.scope_requirements[c.resource_server]] == ["foo"]


def test_add_app_scope(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    c = base_client_class(app=app)

    c.add_app_scope("foo")
    str_list = [str(s) for s in app.scope_requirements[c.resource_server]]
    assert len(str_list) == 2
    assert TransferScopes.all in str_list
    assert "foo" in str_list


def test_add_app_scope_chaining(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    c = base_client_class(app=app).add_app_scope("foo").add_app_scope("bar")
    str_list = [str(s) for s in app.scope_requirements[c.resource_server]]
    assert len(str_list) == 3
    assert TransferScopes.all in str_list
    assert "foo" in str_list
    assert "bar" in str_list


def test_app_mutually_exclusive(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    expected = "A CustomClient cannot use both an 'app' and an 'authorizer'."

    authorizer = NullAuthorizer()
    with pytest.raises(globus_sdk.exc.GlobusSDKUsageError) as ex:
        base_client_class(app=app, authorizer=authorizer)
    assert str(ex.value) == expected


def test_app_name_override(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    c = base_client_class(app=app, app_name="foo")
    assert c.app_name == "foo"


def test_app_scopes_requires_app(base_client_class):
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=r"A CustomClient must have an 'app' to use 'app_scopes'\.",
    ):
        base_client_class(app_scopes=[Scope("foo")])


def test_cannot_double_attach_app(base_client_class):
    app = UserApp("SDK Test", client_id="client_id")
    c = base_client_class(app=app)
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=r"Cannot attach GlobusApp to CustomClient when one is already attached\.",
    ):
        c.attach_globus_app(app)


def test_cannot_attach_app_after_manually_setting_app_scopes(base_client_class):
    c = base_client_class()
    c.app_scopes = [Scope("foo")]
    app = UserApp("SDK Test", client_id="client_id")
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=(
            r"Cannot attach GlobusApp to CustomClient when `app_scopes` is already "
            r"set\."
        ),
    ):
        c.attach_globus_app(app)


def test_cannot_attach_app_when_authorizer_was_provided(base_client_class):
    c = base_client_class(authorizer=NullAuthorizer())
    app = UserApp("SDK Test", client_id="client_id")
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=(
            r"Cannot attach GlobusApp to CustomClient when it has an authorizer "
            r"assigned\."
        ),
    ):
        c.attach_globus_app(app)


def test_cannot_attach_app_when_resource_server_is_not_resolvable():
    class CustomClient(globus_sdk.BaseClient):
        service_name = "transfer"
        default_scope_requirements = [Scope(TransferScopes.all)]

    c = CustomClient()
    app = UserApp("SDK Test", client_id="client_id")
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=(
            r"Unable to use an 'app' with a client with no 'resource_server' defined\."
        ),
    ):
        c.attach_globus_app(app)


def test_cannot_attach_app_with_mismatched_environment(base_client_class):
    c = base_client_class(environment="preview")
    app = UserApp("SDK Test", client_id="client_id")
    with pytest.raises(
        globus_sdk.exc.GlobusSDKUsageError,
        match=(
            r"\[Environment Mismatch\] CustomClient's environment \(preview\) does not "
            r"match the GlobusApp's configured environment \(production\)\."
        ),
    ):
        c.attach_globus_app(app)
