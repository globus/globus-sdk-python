import pytest

import globus_sdk
from globus_sdk.scopes import Scope


def test_specific_flow_client_class_errors_on_scope_access():
    scopes = globus_sdk.SpecificFlowClient.scopes
    assert scopes is not None

    # for the 'user' scope, which is well-defined, we get a special error
    with pytest.raises(AttributeError) as excinfo:
        scopes.user

    err = excinfo.value
    assert (
        "It is not valid to attempt to access the 'scopes' attribute of the "
        "SpecificFlowClient class."
    ) in str(err)

    # but for any other scope we get something a little more generic
    with pytest.raises(AttributeError) as excinfo:
        scopes.demuddle

    err = excinfo.value
    assert str(err).endswith("has no attribute 'demuddle'")


def test_specific_flow_client_class_errors_on_resource_server_access():
    scopes = globus_sdk.SpecificFlowClient.scopes
    assert scopes is not None

    # access via the scopes object raises an error
    with pytest.raises(AttributeError) as excinfo:
        scopes.resource_server

    err = excinfo.value
    assert (
        "It is not valid to attempt to access the 'resource_server' attribute of the "
        "SpecificFlowClient class."
    ) in str(err)

    # and access via the client class raises the same error
    with pytest.raises(AttributeError) as excinfo:
        globus_sdk.SpecificFlowClient.resource_server

    err = excinfo.value
    assert (
        "It is not valid to attempt to access the 'resource_server' attribute of the "
        "SpecificFlowClient class."
    ) in str(err)


def test_specific_flow_client_instance_supports_scope_access():
    client = globus_sdk.SpecificFlowClient("foo")
    scopes = client.scopes
    assert scopes is not None

    # for the 'user' scope, we get a string
    user_scope = scopes.user
    assert isinstance(user_scope, Scope)
    assert str(user_scope).endswith("flow_foo_user")

    # but for any other scope we still get the generic attribute error
    with pytest.raises(AttributeError) as excinfo:
        scopes.demuddle

    err = excinfo.value
    assert str(err).endswith("has no attribute 'demuddle'")


def test_specific_flow_client_instance_supports_resource_server_access():
    client = globus_sdk.SpecificFlowClient("foo")
    resource_server = client.resource_server
    assert isinstance(resource_server, str)
    assert resource_server == "foo"
