import pytest

from globus_sdk.tokenstorage import SQLiteAdapter


def test_sqlite_reading_bad_config():
    adapter = SQLiteAdapter(":memory:")
    # inject bad data (array, needs to be dict)
    # store_config does not check the input type, just uses json.dumps()
    adapter.store_config("foo_conf", [])

    with pytest.raises(ValueError, match="reading config data and got non-dict result"):
        adapter.read_config("foo_conf")
    adapter.close()


def test_sqlite_reading_bad_token_data():
    adapter = SQLiteAdapter(":memory:")
    # inject bad data (array, needs to be dict)
    adapter._connection.execute(
        """\
INSERT INTO token_storage(namespace, resource_server, token_data_json)
VALUES (?, ?, ?)""",
        (adapter.namespace, "foo_rs", "[]"),
    )
    with pytest.raises(
        ValueError, match="data error: token data was not saved as a dict"
    ):
        adapter.get_token_data("foo_rs")
    adapter.close()


def test_sqliteadapter_passes_connect_params():
    with pytest.raises(TypeError):
        SQLiteAdapter(":memory:", connect_params={"invalid_kwarg": True})

    adapter = SQLiteAdapter(":memory:", connect_params={"timeout": 10})
    adapter.close()
