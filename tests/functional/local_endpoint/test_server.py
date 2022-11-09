from globus_sdk import LocalGlobusConnectServer


def test_info_dict_from_nonexistent_file_is_none(tmp_path):
    info_path = tmp_path / "info.json"
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is None


def test_info_dict_from_non_json_file_is_none(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text("{")
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is None


def test_info_dict_from_non_json_object_file_is_none(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text("[]")
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is None


def test_info_dict_from_non_unicode_file_is_none(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_bytes(b'{"foo":"{' + bytes.fromhex("1BAD DEC0DE") + b'}"}')
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is None


def test_info_dict_from_empty_json_file_is_okay_but_has_no_properties(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text("{}")
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is not None
    assert gcs.endpoint_id is None
    assert gcs.domain_name is None


def test_info_dict_can_load_endpoint_id(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text('{"endpoint_id": "foo"}')
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is not None
    assert gcs.endpoint_id == "foo"


def test_info_dict_can_load_domain(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text('{"domain_name": "foo"}')
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is not None
    assert gcs.domain_name == "foo"


def test_endpoint_id_property_ignores_non_str_value(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text('{"endpoint_id": 1}')
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is not None
    assert gcs.endpoint_id is None


def test_domain_name_property_ignores_non_str_value(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text('{"domain_name": ["foo"]}')
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict is not None
    assert gcs.domain_name is None


def test_info_dict_can_reload_with_deleter(tmp_path):
    info_path = tmp_path / "info.json"
    info_path.write_text('{"foo": "bar"}')

    # initial load okay
    gcs = LocalGlobusConnectServer(info_path=info_path)
    assert gcs.info_dict == {"foo": "bar"}
    # update the data on disk
    info_path.write_text('{"bar": "baz"}')
    # data unchanged on the instance
    assert gcs.info_dict == {"foo": "bar"}
    # clear and reload updates the data
    del gcs.info_dict
    assert gcs.info_dict == {"bar": "baz"}
