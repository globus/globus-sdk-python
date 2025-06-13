import pytest

from globus_sdk import (
    MISSING,
    DeleteData,
    GlobusSDKUsageError,
    TransferClient,
    TransferData,
)
from globus_sdk._testing import load_response
from globus_sdk.services.transfer.client import _format_filter
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_transfer_init_simple():
    """
    Creates TransferData objects with and without parameters,
    Verifies TransferData field initialization
    """
    tc = TransferClient()
    meta = load_response(tc.get_submission_id).metadata
    # default init
    tdata = TransferData(tc, GO_EP1_ID, GO_EP2_ID)
    assert tdata["DATA_TYPE"] == "transfer"
    assert tdata["source_endpoint"] == GO_EP1_ID
    assert tdata["destination_endpoint"] == GO_EP2_ID
    assert tdata["submission_id"] == meta["submission_id"]
    assert "DATA" in tdata
    assert len(tdata["DATA"]) == 0


def test_transfer_init_w_params():
    tc = TransferClient()
    meta = load_response(tc.get_submission_id).metadata
    # init with params
    label = "label"
    params = {"param1": "value1", "param2": "value2"}
    tdata = TransferData(
        tc,
        GO_EP1_ID,
        GO_EP2_ID,
        label=label,
        sync_level="exists",
        additional_fields=params,
    )
    assert tdata["label"] == label
    assert tdata["submission_id"] == meta["submission_id"]
    # sync_level of "exists" should be converted to 0
    assert tdata["sync_level"] == 0
    for par in params:
        assert tdata[par] == params[par]


def test_transfer_init_no_client():
    tdata1 = TransferData(None, GO_EP1_ID, GO_EP2_ID)
    tdata2 = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
    tdata3 = TransferData(
        source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID, transfer_client=None
    )
    for tdata in (tdata1, tdata2, tdata3):
        assert tdata["DATA_TYPE"] == "transfer"
        assert tdata["source_endpoint"] == GO_EP1_ID
        assert tdata["destination_endpoint"] == GO_EP2_ID
        assert tdata["submission_id"] is MISSING
        assert "DATA" in tdata
        assert len(tdata["DATA"]) == 0


@pytest.mark.parametrize(
    "tdata_args",
    [
        (),
        (GO_EP1_ID, GO_EP2_ID),
        (MISSING, MISSING, MISSING),
        (MISSING, GO_EP1_ID, MISSING),
        (MISSING, MISSING, GO_EP2_ID),
    ],
)
def test_transfer_init_rejects_bad_usage(tdata_args):
    with pytest.raises(GlobusSDKUsageError):
        TransferData(*tdata_args)


def test_transfer_add_item():
    """
    Adds items to TransferData, verifies results
    """
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
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
    assert data["recursive"] == MISSING
    assert data["external_checksum"] == MISSING
    assert data["checksum_algorithm"] == MISSING

    # add recursive item
    tdata.add_item(source_path, dest_path, recursive=True)
    # verify results
    assert len(tdata["DATA"]) == 2
    r_data = tdata["DATA"][1]
    assert r_data["DATA_TYPE"] == "transfer_item"
    assert r_data["source_path"] == source_path
    assert r_data["destination_path"] == dest_path
    assert r_data["recursive"]
    assert data["external_checksum"] == MISSING
    assert data["checksum_algorithm"] == MISSING

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
    assert c_data["recursive"] == MISSING
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
    assert fields_data["recursive"] == MISSING
    assert all(fields_data[k] == v for k, v in addfields.items())


def test_transfer_add_symlink_item():
    """
    Adds a transfer_symlink_item to TransferData, verifies results
    """
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
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


def test_delete_init_with_client():
    """
    Verifies DeleteData field initialization
    """
    tc = TransferClient()
    load_response(tc.get_submission_id)
    ddata = DeleteData(tc, GO_EP1_ID)
    assert ddata["DATA_TYPE"] == "delete"
    assert ddata["endpoint"] == GO_EP1_ID
    assert "submission_id" in ddata
    assert "DATA" in ddata
    assert len(ddata["DATA"]) == 0


@pytest.mark.parametrize(
    "add_kwargs",
    (
        {"recursive": True},
        {"ignore_missing": True},
        {"interpret_globs": True},
        {"label": "somelabel"},
    ),
)
def test_delete_init_with_supported_parameters(add_kwargs):
    ddata = DeleteData(endpoint=GO_EP1_ID, **add_kwargs)
    for k, v in add_kwargs.items():
        assert ddata[k] == v


def test_delete_init_with_additional_fields():
    params = {"param1": "value1", "param2": "value2"}
    ddata = DeleteData(endpoint=GO_EP1_ID, additional_fields=params)
    assert ddata["param1"] == "value1"
    assert ddata["param2"] == "value2"


@pytest.mark.parametrize(
    "args, kwargs",
    (
        ((None, GO_EP1_ID), {}),
        ((), {"endpoint": GO_EP1_ID}),
        ((), {"endpoint": GO_EP1_ID, "transfer_client": None}),
    ),
)
def test_delete_init_no_client(args, kwargs):
    ddata = DeleteData(*args, **kwargs)
    assert ddata["DATA_TYPE"] == "delete"
    assert ddata["endpoint"] == GO_EP1_ID
    assert ddata["submission_id"] is MISSING
    assert "DATA" in ddata
    assert len(ddata["DATA"]) == 0


@pytest.mark.parametrize(
    "ddata_args", [(), (GO_EP1_ID,), (MISSING, MISSING), (GO_EP1_ID, MISSING)]
)
def test_delete_init_rejects_bad_usage(ddata_args):
    with pytest.raises(GlobusSDKUsageError):
        DeleteData(*ddata_args)


def test_delete_add_item():
    """
    Adds items to DeleteData, verifies results
    """
    ddata = DeleteData(endpoint=GO_EP1_ID)

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


def test_delete_iter_items():
    ddata = DeleteData(endpoint=GO_EP1_ID)
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


def test_transfer_iter_items():
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
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
def test_notification_options(n_succeeded, n_failed, n_inactive):
    notify_kwargs = {}
    if n_succeeded is not None:
        notify_kwargs["notify_on_succeeded"] = n_succeeded
    if n_failed is not None:
        notify_kwargs["notify_on_failed"] = n_failed
    if n_inactive is not None:
        notify_kwargs["notify_on_inactive"] = n_inactive

    ddata = DeleteData(endpoint=GO_EP1_ID, **notify_kwargs)
    tdata = TransferData(
        source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID, **notify_kwargs
    )

    def _default(x):
        return x if x is not None else True

    expect = {
        "notify_on_succeeded": _default(n_succeeded),
        "notify_on_failed": _default(n_failed),
        "notify_on_inactive": _default(n_inactive),
    }
    for k, v in expect.items():
        if k in notify_kwargs:
            assert tdata[k] is v
            assert ddata[k] is v
        else:
            assert tdata[k] is MISSING
            assert ddata[k] is MISSING


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
def test_transfer_sync_levels_result(sync_level, result):
    if isinstance(result, type) and issubclass(result, Exception):
        with pytest.raises(result):
            TransferData(
                source_endpoint=GO_EP1_ID,
                destination_endpoint=GO_EP2_ID,
                sync_level=sync_level,
            )
    else:
        tdata = TransferData(
            source_endpoint=GO_EP1_ID,
            destination_endpoint=GO_EP2_ID,
            sync_level=sync_level,
        )
        assert tdata["sync_level"] == result


@pytest.mark.parametrize("datatype", ("transfer", "delete"))
@pytest.mark.parametrize("value", (None, True, False))
def test_skip_activation_check_supported(datatype, value):
    def create(**kwargs):
        if datatype == "transfer":
            return TransferData(
                source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID, **kwargs
            )
        else:
            return DeleteData(endpoint=GO_EP1_ID, **kwargs)

    if value is None:
        # not present if not provided as a param or provided as explicit None
        assert create()["skip_activation_check"] is MISSING
    elif value:
        data = create(skip_activation_check=True)
        assert "skip_activation_check" in data
        assert data["skip_activation_check"] is True
    else:
        data = create(skip_activation_check=False)
        assert "skip_activation_check" in data
        assert data["skip_activation_check"] is False


def test_add_filter_rule():
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
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
    assert tdata["filter_rules"][1]["type"] == MISSING


@pytest.mark.parametrize(
    "filter,expected",
    [
        ("foo", "foo"),
        ({"foo": "bar", "a": ["b", "c"]}, "foo:bar/a:b,c"),
        (
            [
                "foo",
                {
                    "a": ["b", "c"],
                },
            ],
            ["foo", "a:b,c"],
        ),
    ],
)
def test_ls_format_filter(filter, expected):
    assert _format_filter(filter) == expected
