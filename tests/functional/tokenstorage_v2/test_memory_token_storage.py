from globus_sdk.experimental.tokenstorage import MemoryTokenStorage


def test_store_and_get_token_data_by_resource_server(
    mock_token_data_by_resource_server,
):
    adapter = MemoryTokenStorage()
    adapter.store_token_data_by_resource_server(mock_token_data_by_resource_server)

    gotten = adapter.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        assert (
            mock_token_data_by_resource_server[resource_server].to_dict()
            == gotten[resource_server].to_dict()
        )


def test_store_token_response_with_namespace(mock_response):
    adapter = MemoryTokenStorage(namespace="foo")
    adapter.store_token_response(mock_response)

    assert (
        adapter._tokens["foo"]["resource_server_1"]["access_token"] == "access_token_1"
    )
    assert (
        adapter._tokens["foo"]["resource_server_2"]["access_token"] == "access_token_2"
    )


def test_get_token_data(mock_response):
    adapter = MemoryTokenStorage()
    adapter.store_token_response(mock_response)

    assert adapter.get_token_data("resource_server_1").access_token == "access_token_1"
    assert adapter.get_token_data("resource_server_2").access_token == "access_token_2"


def test_remove_token_data(mock_response):
    adapter = MemoryTokenStorage()
    adapter.store_token_response(mock_response)

    # remove rs1, confirm only rs2 is still available
    remove_result = adapter.remove_token_data("resource_server_1")
    assert remove_result is True

    assert adapter.get_token_data("resource_server_1") is None
    assert adapter.get_token_data("resource_server_2").access_token == "access_token_2"

    # confirm unable to re-remove rs1
    remove_result = adapter.remove_token_data("resource_server_1")
    assert remove_result is False
