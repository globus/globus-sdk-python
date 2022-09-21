import json

import pytest

from globus_sdk.tokenstorage import SimpleJSONFileAdapter, SQLiteAdapter
from globus_sdk.version import __version__ as sdkversion


def test_sqlite_reading_bad_config():
    adapter = SQLiteAdapter(":memory:")
    # inject bad data (array, needs to be dict)
    # store_config does not check the input type, just uses json.dumps()
    adapter.store_config("foo_conf", [])

    with pytest.raises(ValueError, match="reading config data and got non-dict result"):
        adapter.read_config("foo_conf")


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


def test_sqliteadapter_passes_connect_params():
    with pytest.raises(TypeError):
        SQLiteAdapter(":memory:", connect_params={"invalid_kwarg": True})

    SQLiteAdapter(":memory:", connect_params={"timeout": 10})


def test_simplejson_reading_bad_data(tmp_path):
    # non-dict data at root
    foo_file = tmp_path / "foo.json"
    foo_file.write_text('["foobar"]')
    foo_adapter = SimpleJSONFileAdapter(str(foo_file))

    with pytest.raises(ValueError, match="reading from json file got non-dict data"):
        foo_adapter.get_by_resource_server()

    # non-dict data in 'by_rs'

    bar_file = tmp_path / "bar.json"
    bar_file.write_text(
        json.dumps(
            {"by_rs": [], "format_version": "1.0", "globus-sdk.version": sdkversion}
        )
    )
    bar_adapter = SimpleJSONFileAdapter(str(bar_file))

    with pytest.raises(ValueError, match="existing data file is malformed"):
        bar_adapter.get_by_resource_server()


def test_simplejson_reading_unsupported_format_version(tmp_path):
    # data appears valid, but lists a value for "format_version" which instructs the
    # adapter explicitly that it is in a format which is unknown / not supported
    foo_file = tmp_path / "foo.json"
    foo_file.write_text(
        json.dumps(
            {"by_rs": {}, "format_version": "0.0", "globus-sdk.version": sdkversion}
        )
    )
    adapter = SimpleJSONFileAdapter(str(foo_file))

    with pytest.raises(ValueError, match="existing data file is in an unknown format"):
        adapter.get_by_resource_server()
