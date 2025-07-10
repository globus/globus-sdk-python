import base64
import os
import shutil
import uuid

import pytest

import globus_sdk
from globus_sdk.testing import load_response

_IS_WINDOWS = os.name == "nt"

ID_ZERO = uuid.UUID(int=0)


def _compute_base32_id(value):
    """
    Create a base32-encoded UUID in the format used by legacy Globus systems to
    represent Identity IDs as unix-friendly usernames.
    GCP CN values still match this format.
    """
    if isinstance(value, str):
        value = uuid.UUID(value)
    encoded_bytes = base64.b32encode(value.bytes)
    result = encoded_bytes.decode()
    result = result.rstrip("=").lower()
    return f"u_{result}"


def _compute_confdir(homedir, alt=False):
    if alt:
        return os.path.join(homedir, "alt-conf-dir/lta")
    if _IS_WINDOWS:
        return os.path.join(homedir, "Globus Connect")
    else:
        return os.path.join(homedir, ".globusonline/lta")


def normalize_config_dir_argument(config_dir):
    return config_dir if _IS_WINDOWS else os.path.dirname(config_dir)


@pytest.fixture
def mocked_confdir(tmp_path):
    confdir = _compute_confdir(tmp_path)
    os.makedirs(confdir)
    return confdir


@pytest.fixture
def mocked_alternate_confdir(tmp_path):
    altconfdir = _compute_confdir(tmp_path, alt=True)
    os.makedirs(altconfdir)
    return altconfdir


@pytest.fixture(autouse=True)
def mocked_homedir(monkeypatch, tmp_path, mocked_confdir, mocked_alternate_confdir):
    def mock_expanduser(path):
        return str(tmp_path / path.replace("~/", ""))

    if _IS_WINDOWS:
        monkeypatch.setitem(os.environ, "LOCALAPPDATA", str(tmp_path))
    else:
        monkeypatch.setattr(os.path, "expanduser", mock_expanduser)


@pytest.fixture
def write_gcp_id_file(mocked_confdir, mocked_alternate_confdir):
    def _func_fixture(epid, alternate=False):
        fpath = os.path.join(
            mocked_alternate_confdir if alternate else mocked_confdir, "client-id.txt"
        )
        with open(fpath, "w") as f:
            f.write(epid)
            f.write("\n")

    return _func_fixture


@pytest.fixture
def write_gridmap(mocked_confdir):
    def _func_fixture(data, alternate=False):
        fpath = os.path.join(
            mocked_alternate_confdir if alternate else mocked_confdir, "gridmap"
        )
        with open(fpath, "w") as f:
            f.write(data)

    return _func_fixture


@pytest.fixture
def local_gcp():
    return globus_sdk.LocalGlobusConnectPersonal()


@pytest.fixture
def auth_client():
    return globus_sdk.AuthClient()


@pytest.mark.skipif(not _IS_WINDOWS, reason="test requires Windows")
def test_localep_localappdata_notset(local_gcp, monkeypatch):
    monkeypatch.delitem(os.environ, "LOCALAPPDATA")
    with pytest.raises(globus_sdk.GlobusSDKUsageError):
        local_gcp.endpoint_id


def test_localep_load_id(local_gcp, write_gcp_id_file):
    assert local_gcp.endpoint_id is None
    write_gcp_id_file("foobar")
    assert local_gcp.endpoint_id == "foobar"
    write_gcp_id_file("xyz")
    assert local_gcp.endpoint_id == "foobar"
    del local_gcp.endpoint_id
    assert local_gcp.endpoint_id == "xyz"


def test_localep_load_id_alternate_conf_dir(
    mocked_alternate_confdir, write_gcp_id_file
):
    gcp = globus_sdk.LocalGlobusConnectPersonal(
        config_dir=normalize_config_dir_argument(mocked_alternate_confdir)
    )
    assert gcp.endpoint_id is None
    write_gcp_id_file("foobar", alternate=True)
    assert gcp.endpoint_id == "foobar"
    write_gcp_id_file("xyz", alternate=True)
    assert gcp.endpoint_id == "foobar"
    del gcp.endpoint_id
    assert gcp.endpoint_id == "xyz"


def test_load_id_no_confdir(local_gcp, mocked_confdir, mocked_alternate_confdir):
    shutil.rmtree(mocked_confdir)
    shutil.rmtree(mocked_alternate_confdir)
    alt_gcp = globus_sdk.LocalGlobusConnectPersonal(config_dir=mocked_alternate_confdir)
    assert local_gcp.endpoint_id is None
    assert alt_gcp.endpoint_id is None


def test_get_owner_info(local_gcp, write_gridmap, auth_client):
    meta = load_response(auth_client.get_identities, case="globusid").metadata
    local_username = meta["short_username"]
    write_gridmap(
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/'
        f'CN={local_username}" {local_username}\n'
    )
    info = local_gcp.get_owner_info()
    assert isinstance(info, globus_sdk.GlobusConnectPersonalOwnerInfo)
    assert info.username == meta["username"]
    assert info.id is None
    assert str(info) == f"GlobusConnectPersonalOwnerInfo(username={info.username})"

    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == meta["id"]


def test_get_owner_info_b32_mode(local_gcp, write_gridmap, auth_client):
    meta = load_response(auth_client.get_identities).metadata
    base32_id = _compute_base32_id(meta["id"])
    local_username = meta["username"].partition("@")[0]
    write_gridmap(
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/'
        f'CN={base32_id}" {local_username}\n'
    )
    info = local_gcp.get_owner_info()
    assert isinstance(info, globus_sdk.GlobusConnectPersonalOwnerInfo)
    assert info.username is None
    assert info.id == meta["id"]

    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == meta["id"]
    assert data["username"] == meta["username"]


# these things are close to the right thing, but each is somehow wrong
@pytest.mark.parametrize(
    "cn",
    [
        # no 'u_'
        _compute_base32_id(ID_ZERO)[2:],
        # short one char
        _compute_base32_id(ID_ZERO)[:-1],
        # invalid b32 char included
        _compute_base32_id(ID_ZERO)[:-1] + "/",
    ],
)
def test_get_owner_info_b32_mode_invalid_data(
    local_gcp, write_gridmap, cn, auth_client
):
    write_gridmap(
        f'"/C=US/O=Globus Consortium/OU=Globus Connect User/CN={cn}" javert\n'
    )
    info = local_gcp.get_owner_info()
    assert isinstance(info, globus_sdk.GlobusConnectPersonalOwnerInfo)
    assert info.username == f"{cn}@globusid.org"


@pytest.mark.parametrize(
    "bad_cn_line",
    [
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=koala"',
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=koala" panda fossa',
        "",
        '"" koala',
    ],
)
def test_get_owner_info_malformed_entry(local_gcp, write_gridmap, bad_cn_line):
    write_gridmap(bad_cn_line + "\n")
    assert local_gcp.get_owner_info() is None


def test_get_owner_info_no_conf(local_gcp):
    assert local_gcp.get_owner_info() is None
    assert local_gcp.get_owner_info(auth_client) is None


def test_get_owner_info_no_confdir(local_gcp, mocked_confdir, auth_client):
    shutil.rmtree(mocked_confdir)
    assert local_gcp.get_owner_info() is None
    assert local_gcp.get_owner_info(auth_client) is None


def test_get_owner_info_multiline_data(local_gcp, write_gridmap, auth_client):
    meta = load_response(auth_client.get_identities, case="globusid").metadata
    local_username = meta["short_username"]
    write_gridmap(
        "\n".join(
            [
                (
                    '"/C=US/O=Globus Consortium/OU=Globus Connect User/'
                    f'CN={local_username}{x}" {local_username}{x}'
                )
                for x in ["", "2", "3"]
            ]
        )
        + "\n"
    )
    info = local_gcp.get_owner_info()
    assert isinstance(info, globus_sdk.GlobusConnectPersonalOwnerInfo)
    assert info.username == meta["username"]

    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == meta["id"]


def test_get_owner_info_no_auth_data(local_gcp, write_gridmap, auth_client):
    load_response(auth_client.get_identities, case="empty")
    write_gridmap(
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=azathoth" azathoth\n'
    )
    info = local_gcp.get_owner_info()
    assert isinstance(info, globus_sdk.GlobusConnectPersonalOwnerInfo)
    assert info.username == "azathoth@globusid.org"

    data = local_gcp.get_owner_info(auth_client)
    assert data is None


def test_get_owner_info_gridmap_permission_denied(local_gcp, mocked_confdir):
    fpath = os.path.join(mocked_confdir, "gridmap")
    if not _IS_WINDOWS:
        with open(fpath, "w"):  # "touch"
            pass
        os.chmod(fpath, 0o000)
    else:
        # on windows, trying to read a directory gets a permission error
        # this is just an easy way for tests to simulate bad permissions
        os.makedirs(fpath)

    with pytest.raises(PermissionError):
        local_gcp.get_owner_info()


def test_get_endpoint_id_permission_denied(local_gcp, mocked_confdir):
    fpath = os.path.join(mocked_confdir, "client-id.txt")
    if not _IS_WINDOWS:
        with open(fpath, "w"):  # "touch"
            pass
        os.chmod(fpath, 0o000)
    else:
        # on windows, trying to read a directory gets a permission error
        # this is just an easy way for tests to simulate bad permissions
        os.makedirs(fpath)

    with pytest.raises(PermissionError):
        local_gcp.endpoint_id
