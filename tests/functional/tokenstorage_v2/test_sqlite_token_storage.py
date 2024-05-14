import os

import pytest

from globus_sdk.experimental.tokenstorage import SQLiteTokenStorage
from globus_sdk.tokenstorage import SQLiteAdapter


@pytest.fixture
def db_filename(tempdir):
    return os.path.join(tempdir, "test.db")


MEMORY_DBNAME = ":memory:"


@pytest.fixture
def adapters_to_close():
    data = set()
    yield data
    for x in data:
        x.close()


@pytest.fixture
def make_adapter(adapters_to_close):
    def func(*args, **kwargs):
        ret = SQLiteTokenStorage(*args, **kwargs)
        adapters_to_close.add(ret)
        return ret

    return func


@pytest.mark.parametrize(
    "success, use_file, kwargs",
    [
        (False, False, {}),
        (False, False, {"namespace": "foo"}),
        (True, False, {"dbname": MEMORY_DBNAME}),
        (True, False, {"dbname": MEMORY_DBNAME, "namespace": "foo"}),
        (True, True, {}),
        (True, True, {"namespace": "foo"}),
        (False, True, {"dbname": MEMORY_DBNAME}),
        (False, True, {"dbname": MEMORY_DBNAME, "namespace": "foo"}),
    ],
)
def test_constructor(success, use_file, kwargs, db_filename, make_adapter):
    if success:
        if use_file:
            make_adapter(db_filename, **kwargs)
        else:
            make_adapter(**kwargs)
    else:
        with pytest.raises(TypeError):
            if use_file:
                make_adapter(db_filename, **kwargs)
            else:
                make_adapter(**kwargs)


def test_store_and_retrieve_simple_config(make_adapter):
    adapter = make_adapter(MEMORY_DBNAME)
    store_val = {"val1": True, "val2": None, "val3": 1.4}
    adapter.store_config("myconf", store_val)
    read_val = adapter.read_config("myconf")
    assert read_val == store_val
    assert read_val is not store_val


def test_store_and_get_token_data_by_resource_server(
    mock_token_data_by_resource_server, make_adapter
):
    adapter = make_adapter(MEMORY_DBNAME)
    adapter.store_token_data_by_resource_server(mock_token_data_by_resource_server)

    gotten = adapter.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        assert (
            mock_token_data_by_resource_server[resource_server].to_dict()
            == gotten[resource_server].to_dict()
        )


def test_multiple_adapters_store_and_retrieve(mock_response, db_filename, make_adapter):
    adapter1 = make_adapter(db_filename)
    adapter2 = make_adapter(db_filename)
    adapter1.store_token_response(mock_response)

    assert adapter2.get_token_data("resource_server_1").access_token == "access_token_1"
    assert adapter2.get_token_data("resource_server_2").access_token == "access_token_2"


def test_multiple_adapters_store_and_retrieve_different_namespaces(
    mock_response, db_filename, make_adapter
):
    adapter1 = make_adapter(db_filename, namespace="foo")
    adapter2 = make_adapter(db_filename, namespace="bar")
    adapter1.store_token_response(mock_response)

    data = adapter2.get_token_data_by_resource_server()
    assert data == {}


def test_load_missing_config_data(make_adapter):
    adapter = make_adapter(MEMORY_DBNAME)
    assert adapter.read_config("foo") is None


def test_load_missing_token_data(make_adapter):
    adapter = make_adapter(MEMORY_DBNAME)
    assert adapter.get_token_data_by_resource_server() == {}
    assert adapter.get_token_data("resource_server_1") is None


def test_remove_tokens(mock_response, make_adapter):
    adapter = make_adapter(MEMORY_DBNAME)
    adapter.store_token_response(mock_response)

    removed = adapter.remove_token_data("resource_server_1")
    assert removed
    assert adapter.get_token_data("resource_server_1") is None
    assert adapter.get_token_data("resource_server_2").access_token == "access_token_2"

    removed = adapter.remove_token_data("resource_server_1")
    assert not removed


def test_remove_config(make_adapter):
    adapter = make_adapter(MEMORY_DBNAME)
    store_val = {"val1": True, "val2": None, "val3": 1.4}
    adapter.store_config("myconf", store_val)
    adapter.store_config("myconf2", store_val)
    removed = adapter.remove_config("myconf")
    assert removed
    read_val = adapter.read_config("myconf")
    assert read_val is None
    read_val = adapter.read_config("myconf2")
    assert read_val == store_val

    removed = adapter.remove_config("myconf")
    assert not removed


def test_iter_namespaces(mock_response, db_filename, make_adapter):
    foo_adapter = make_adapter(db_filename, namespace="foo")
    bar_adapter = make_adapter(db_filename, namespace="bar")
    baz_adapter = make_adapter(db_filename, namespace="baz")

    for adapter in [foo_adapter, bar_adapter, baz_adapter]:
        assert list(adapter.iter_namespaces()) == []
        assert list(adapter.iter_namespaces(include_config_namespaces=True)) == []

    foo_adapter.store_token_response(mock_response)

    for adapter in [foo_adapter, bar_adapter, baz_adapter]:
        assert list(adapter.iter_namespaces()) == ["foo"]
        assert list(adapter.iter_namespaces(include_config_namespaces=True)) == ["foo"]

    bar_adapter.store_token_response(mock_response)

    for adapter in [foo_adapter, bar_adapter, baz_adapter]:
        assert set(adapter.iter_namespaces()) == {"foo", "bar"}
        assert set(adapter.iter_namespaces(include_config_namespaces=True)) == {
            "foo",
            "bar",
        }

    baz_adapter.store_config("some_conf", {})

    for adapter in [foo_adapter, bar_adapter, baz_adapter]:
        assert set(adapter.iter_namespaces()) == {"foo", "bar"}
        assert set(adapter.iter_namespaces(include_config_namespaces=True)) == {
            "foo",
            "bar",
            "baz",
        }


def test_backwards_compatible_storage(mock_response, db_filename, make_adapter):
    # store data with SQLiteAdapter
    old_adapter = SQLiteAdapter(db_filename)
    old_adapter.store(mock_response)
    old_adapter.close()

    # retrieve data with SQLiteTokenStorage using the same file
    new_adapter = make_adapter(db_filename)
    assert (
        new_adapter.get_token_data("resource_server_1").access_token == "access_token_1"
    )
    assert (
        new_adapter.get_token_data("resource_server_2").access_token == "access_token_2"
    )
