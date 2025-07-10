import json

import pytest

from globus_sdk import __version__ as sdkversion
from globus_sdk.token_storage import SimpleJSONFileAdapter


def test_simplejson_reading_bad_data(tmp_path):
    # non-dict data at root
    foo_file = tmp_path / "foo.json"
    foo_file.write_text('["foobar"]')
    foo_adapter = SimpleJSONFileAdapter(str(foo_file))

    with pytest.raises(ValueError, match="Found non-dict root data while loading"):
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
