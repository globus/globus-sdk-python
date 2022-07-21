import pytest

import globus_sdk
from globus_sdk._testing import load_response
from tests.common import GO_EP1_ID, GO_EP2_ID


@pytest.fixture
def client():
    tc = globus_sdk.TransferClient()
    load_response(tc.get_submission_id)
    return tc


@pytest.fixture
def transfer_data(client):
    def _transfer_data(**kwargs):
        return globus_sdk.TransferData(client, GO_EP1_ID, GO_EP2_ID, **kwargs)

    return _transfer_data


@pytest.fixture
def delete_data(client):
    def _delete_data(**kwargs):
        return globus_sdk.DeleteData(client, GO_EP1_ID, **kwargs)

    return _delete_data


def test_tranfer_init(transfer_data):
    """
    Creates TransferData objects with and without parameters,
    Verifies TransferData field initialization
    """
    # default init
    tdata = transfer_data()
    assert tdata["DATA_TYPE"] == "transfer"
    assert tdata["source_endpoint"] == GO_EP1_ID
    assert tdata["destination_endpoint"] == GO_EP2_ID
    assert "submission_id" in tdata
    assert "DATA" in tdata
    assert len(tdata["DATA"]) == 0

    # init with params
    label = "label"
    params = {"param1": "value1", "param2": "value2"}
    param_tdata = transfer_data(
        label=label, sync_level="exists", additional_fields=params
    )
    assert param_tdata["label"] == label
    # sync_level of "exists" should be converted to 0
    assert param_tdata["sync_level"] == 0
    for par in params:
        assert param_tdata[par] == params[par]


def test_transfer_add_item(transfer_data):
    """
    Adds items to TransferData, verifies results
    """
    tdata = transfer_data()
    # add item
    source_path = "source/path/"
    dest_path = "dest/path/"
    tdata.add_item(source_path, dest_path)
    # verify results
    assert len(tdata["DATA"]) == 1
    data = tdata["DATA"][0]
    assert data["DATA_TYPE"] == "transfer_item"
    assert data["source_path"] == source_path
    assert data["destination_path"] == dest_path
    assert not data["recursive"]
    assert data["external_checksum"] is None
    assert data["checksum_algorithm"] is None

    # add recursive item
    tdata.add_item(source_path, dest_path, recursive=True)
    # verify results
    assert len(tdata["DATA"]) == 2
    r_data = tdata["DATA"][1]
    assert r_data["DATA_TYPE"] == "transfer_item"
    assert r_data["source_path"] == source_path
    assert r_data["destination_path"] == dest_path
    assert r_data["recursive"]
    assert r_data["external_checksum"] is None
    assert r_data["checksum_algorithm"] is None

    # item with checksum
    checksum = "d577273ff885c3f84dadb8578bb41399"
    algorithm = "MD5"
    tdata.add_item(
        source_path, dest_path, external_checksum=checksum, checksum_algorithm=algorithm
    )
    assert len(tdata["DATA"]) == 3
    c_data = tdata["DATA"][2]
    assert c_data["DATA_TYPE"] == "transfer_item"
    assert c_data["source_path"] == source_path
    assert c_data["destination_path"] == dest_path
    assert not c_data["recursive"]
    assert c_data["external_checksum"] == checksum
    assert c_data["checksum_algorithm"] == algorithm

    # add an item which uses `additional_fields`
    addfields = {"foo": "bar", "bar": "baz"}
    tdata.add_item(source_path, dest_path, additional_fields=addfields)
    assert len(tdata["DATA"]) == 4
    fields_data = tdata["DATA"][3]
    assert fields_data["DATA_TYPE"] == "transfer_item"
    assert fields_data["source_path"] == source_path
    assert fields_data["destination_path"] == dest_path
    assert not fields_data["recursive"]
    assert all(fields_data[k] == v for k, v in addfields.items())


def test_transfer_add_symlink_item(transfer_data):
    """
    Adds a transfer_symlink_item to TransferData, verifies results
    """
    tdata = transfer_data()
    # add item
    source_path = "source/path/"
    dest_path = "dest/path/"
    tdata.add_symlink_item(source_path, dest_path)
    # verify results
    assert len(tdata["DATA"]) == 1
    data = tdata["DATA"][0]
    assert data["DATA_TYPE"] == "transfer_symlink_item"
    assert data["source_path"] == source_path
    assert data["destination_path"] == dest_path


def test_delete_init(delete_data):
    """
    Verifies DeleteData field initialization
    """
    # default init
    default_ddata = delete_data()
    assert default_ddata["DATA_TYPE"] == "delete"
    assert default_ddata["endpoint"] == GO_EP1_ID
    assert "submission_id" in default_ddata
    assert "DATA" in default_ddata
    assert len(default_ddata["DATA"]) == 0

    # init with params
    label = "label"
    params = {"param1": "value1", "param2": "value2"}
    param_ddata = delete_data(label=label, recursive="True", additional_fields=params)
    assert param_ddata["label"] == label
    assert param_ddata["recursive"] == "True"
    for par in params:
        assert param_ddata[par] == params[par]


def test_delete_add_item(delete_data):
    """
    Adds items to DeleteData, verifies results
    """
    ddata = delete_data()

    # add normal item
    path = "source/path/"
    ddata.add_item(path)
    assert len(ddata["DATA"]) == 1
    data = ddata["DATA"][0]
    assert data["DATA_TYPE"] == "delete_item"
    assert data["path"] == path

    # add an item which uses `additional_fields`
    addfields = {"foo": "bar", "bar": "baz"}
    ddata.add_item(path, additional_fields=addfields)
    assert len(ddata["DATA"]) == 2
    fields_data = ddata["DATA"][1]
    assert fields_data["DATA_TYPE"] == "delete_item"
    assert fields_data["path"] == path
    assert all(fields_data[k] == v for k, v in addfields.items())


def test_delete_iter_items(delete_data):
    ddata = delete_data()
    # add item
    ddata.add_item("abc/")
    ddata.add_item("def/")

    # order preserved, well-formed
    as_list = list(ddata.iter_items())
    assert len(as_list) == 2

    def check_item(x, path):
        assert isinstance(x, dict)
        assert x.get("DATA_TYPE") == "delete_item"
        assert x.get("path") == path

    check_item(as_list[0], "abc/")
    check_item(as_list[1], "def/")


def test_transfer_iter_items(transfer_data):
    tdata = transfer_data()
    tdata.add_item("source/abc.txt", "dest/abc.txt")
    tdata.add_item("source/def/", "dest/def/", recursive=True)

    # order preserved, well-formed
    as_list = list(tdata.iter_items())
    assert len(as_list) == 2

    def check_item(x, src, dst, params=None):
        params = params or {}
        assert isinstance(x, dict)
        assert x.get("DATA_TYPE") == "transfer_item"
        assert x.get("source_path") == src
        assert x.get("destination_path") == dst
        for k, v in params.items():
            assert x.get(k) == v

    check_item(as_list[0], "source/abc.txt", "dest/abc.txt")
    check_item(as_list[1], "source/def/", "dest/def/", {"recursive": True})


@pytest.mark.parametrize("n_succeeded", [None, True, False])
@pytest.mark.parametrize("n_failed", [None, True, False])
@pytest.mark.parametrize("n_inactive", [None, True, False])
def test_notification_options(
    transfer_data, delete_data, n_succeeded, n_failed, n_inactive
):
    notify_kwargs = {}
    if n_succeeded is not None:
        notify_kwargs["notify_on_succeeded"] = n_succeeded
    if n_failed is not None:
        notify_kwargs["notify_on_failed"] = n_failed
    if n_inactive is not None:
        notify_kwargs["notify_on_inactive"] = n_inactive

    ddata = delete_data(**notify_kwargs)
    tdata = transfer_data(**notify_kwargs)

    def _default(x):
        return x if x is not None else True

    expect = {
        "notify_on_succeeded": _default(n_succeeded),
        "notify_on_failed": _default(n_failed),
        "notify_on_inactive": _default(n_inactive),
    }
    for k, v in expect.items():
        assert tdata[k] is v
        assert ddata[k] is v


@pytest.mark.parametrize(
    "sync_level, result",
    [
        ("exists", 0),
        (0, 0),
        ("size", 1),
        (1, 1),
        ("mtime", 2),
        (2, 2),
        ("checksum", 3),
        (3, 3),
        ("EXISTS", ValueError),
        ("hash", ValueError),
        (100, 100),
    ],
)
def test_tranfer_sync_levels_result(transfer_data, sync_level, result):
    if isinstance(result, type) and issubclass(result, Exception):
        with pytest.raises(result):
            transfer_data(sync_level=sync_level)
    else:
        tdata = transfer_data(sync_level=sync_level)
        assert tdata["sync_level"] == result


def test_skip_activation_check_supported(transfer_data, delete_data):
    # default, false
    tdata = transfer_data()
    ddata = delete_data()
    for data in [tdata, ddata]:
        assert "skip_activation_check" in data
        assert data["skip_activation_check"] is False

    # can set to True
    tdata = transfer_data(skip_activation_check=True)
    ddata = delete_data(skip_activation_check=True)
    for data in [tdata, ddata]:
        assert "skip_activation_check" in data
        assert data["skip_activation_check"] is True


def test_add_filter_rule(transfer_data):
    tdata = transfer_data()
    assert "filter_rules" not in tdata

    tdata.add_filter_rule("*.tgz", type="file")
    assert "filter_rules" in tdata
    assert isinstance(tdata["filter_rules"], list)
    assert len(tdata["filter_rules"]) == 1
    assert tdata["filter_rules"][0]["DATA_TYPE"] == "filter_rule"
    assert tdata["filter_rules"][0]["method"] == "exclude"
    assert tdata["filter_rules"][0]["name"] == "*.tgz"
    assert tdata["filter_rules"][0]["type"] == "file"

    tdata.add_filter_rule("tmp")
    assert len(tdata["filter_rules"]) == 2
    assert tdata["filter_rules"][1]["DATA_TYPE"] == "filter_rule"
    assert tdata["filter_rules"][1]["method"] == "exclude"
    assert tdata["filter_rules"][1]["name"] == "tmp"
    assert "type" not in tdata["filter_rules"][1]
