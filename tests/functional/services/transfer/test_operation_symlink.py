import uuid

import pytest

from globus_sdk import exc
from globus_sdk.testing import RegisteredResponse


@pytest.fixture
def symlink_endpoint_id():
    return str(uuid.uuid1())


@pytest.fixture(autouse=True)
def _setup_symlink_response(symlink_endpoint_id):
    RegisteredResponse(
        service="transfer",
        method="POST",
        path=f"/v0.10/operation/endpoint/{symlink_endpoint_id}/symlink",
        json={},
    ).add()


def test_operation_symlink_warns(client, symlink_endpoint_id):
    with pytest.warns(
        exc.RemovedInV4Warning,
        match="operation_symlink is not currently supported by any collections",
    ):
        client.operation_symlink(symlink_endpoint_id, "some_link_target", "/some/path")
