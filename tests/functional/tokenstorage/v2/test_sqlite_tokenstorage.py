import pytest

from globus_sdk import exc
from globus_sdk.token_storage import SQLiteAdapter, SQLiteTokenStorage


@pytest.fixture
def db_file(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def adapters_to_close():
    data = set()
    yield data
    for x in data:
        x.close()


@pytest.fixture
def make_adapter(adapters_to_close, db_file):
    def func(*args, **kwargs):
        if len(args) == 0 and "filepath" not in kwargs:
            args = (db_file,)
        ret = SQLiteTokenStorage(*args, **kwargs)
        adapters_to_close.add(ret)
        return ret

    return func


@pytest.mark.parametrize("kwargs", [{}, {"namespace": "foo"}])
def test_constructor(kwargs, db_file, make_adapter):
    make_adapter(db_file, **kwargs)
    assert db_file.exists()


def test_constructor_rejects_memory_db(make_adapter):
    with pytest.raises(
        exc.GlobusSDKUsageError,
        match="SQLiteTokenStorage cannot be used with a ':memory:' database",
    ):
        make_adapter(":memory:")


def test_store_and_get_token_data_by_resource_server(
    mock_token_data_by_resource_server, make_adapter
):
    adapter = make_adapter()
    adapter.store_token_data_by_resource_server(mock_token_data_by_resource_server)

    gotten = adapter.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        assert (
            mock_token_data_by_resource_server[resource_server].to_dict()
            == gotten[resource_server].to_dict()
        )


def test_multiple_adapters_store_and_retrieve(mock_response, db_file, make_adapter):
    adapter1 = make_adapter(db_file)
    adapter2 = make_adapter(db_file)
    adapter1.store_token_response(mock_response)

    assert adapter2.get_token_data("resource_server_1").access_token == "access_token_1"
    assert adapter2.get_token_data("resource_server_2").access_token == "access_token_2"


def test_multiple_adapters_store_and_retrieve_different_namespaces(
    mock_response, db_file, make_adapter
):
    adapter1 = make_adapter(db_file, namespace="foo")
    adapter2 = make_adapter(db_file, namespace="bar")
    adapter1.store_token_response(mock_response)

    data = adapter2.get_token_data_by_resource_server()
    assert data == {}


def test_load_missing_token_data(make_adapter):
    adapter = make_adapter()
    assert adapter.get_token_data_by_resource_server() == {}
    assert adapter.get_token_data("resource_server_1") is None


def test_remove_tokens(mock_response, make_adapter):
    adapter = make_adapter()
    adapter.store_token_response(mock_response)

    removed = adapter.remove_token_data("resource_server_1")
    assert removed
    assert adapter.get_token_data("resource_server_1") is None
    assert adapter.get_token_data("resource_server_2").access_token == "access_token_2"

    removed = adapter.remove_token_data("resource_server_1")
    assert not removed


def test_iter_namespaces(mock_response, db_file, make_adapter):
    foo_adapter = make_adapter(db_file, namespace="foo")
    bar_adapter = make_adapter(db_file, namespace="bar")

    for adapter in [foo_adapter, bar_adapter]:
        assert list(adapter.iter_namespaces()) == []

    foo_adapter.store_token_response(mock_response)

    for adapter in [foo_adapter, bar_adapter]:
        assert list(adapter.iter_namespaces()) == ["foo"]

    bar_adapter.store_token_response(mock_response)

    for adapter in [foo_adapter, bar_adapter]:
        assert set(adapter.iter_namespaces()) == {"foo", "bar"}


def test_migrate_from_v1_adapter(mock_response, db_file, make_adapter):
    # store data with SQLiteAdapter
    old_adapter = SQLiteAdapter(db_file)
    old_adapter.store(mock_response)
    old_adapter.close()

    # retrieve data with SQLiteTokenStorage using the same file
    new_adapter = make_adapter(db_file)
    assert (
        new_adapter.get_token_data("resource_server_1").access_token == "access_token_1"
    )
    assert (
        new_adapter.get_token_data("resource_server_2").access_token == "access_token_2"
    )
