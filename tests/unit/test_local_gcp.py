import os

import pytest

from globus_sdk import GlobusSDKUsageError, LocalGlobusConnectPersonal


@pytest.fixture
def pretend_is_windows(monkeypatch):
    """Patch LocalGlobusConnectPersonal to think it's on Windows
    *even if it isn't*.
    """
    monkeypatch.setattr(
        "globus_sdk.local_endpoint.personal.endpoint._on_windows", lambda: True
    )


@pytest.fixture
def pretend_is_not_windows(monkeypatch):
    """Patch LocalGlobusConnectPersonal to think it's NOT on Windows
    *even if it is*.
    """
    monkeypatch.setattr(
        "globus_sdk.local_endpoint.personal.endpoint._on_windows", lambda: False
    )


def test_windows_config_dir_requires_localappdata(pretend_is_windows, monkeypatch):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    gcp = LocalGlobusConnectPersonal()
    with pytest.raises(GlobusSDKUsageError):
        gcp.config_dir


def test_windows_config_dir_ignores_localappdata_with_explicit_init(
    pretend_is_windows, monkeypatch
):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    gcp = LocalGlobusConnectPersonal(config_dir="/foo/bar")
    assert gcp.config_dir == "/foo/bar"


def test_windows_default_config_dir(pretend_is_windows, monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    gcp = LocalGlobusConnectPersonal()
    assert gcp.config_dir == str(tmp_path / "Globus Connect")


def test_nonwindows_default_config_dir(pretend_is_not_windows, monkeypatch, tmp_path):
    def _fake_expanduser(p: str):
        assert p.startswith("~/")
        return str(tmp_path / p[2:])

    monkeypatch.setattr(os.path, "expanduser", _fake_expanduser)
    gcp = LocalGlobusConnectPersonal()
    assert gcp.config_dir == str(tmp_path / ".globusonline")
