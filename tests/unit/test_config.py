import os
import pathlib
from unittest import mock

import pytest

import globus_sdk.config


def test_get_service_url():
    """
    Confirms get_service_url returns expected results
    Tests environments, services, and missing values
    """
    assert (
        globus_sdk.config.get_service_url("auth", environment="production")
        == "https://auth.globus.org/"
    )
    assert (
        globus_sdk.config.get_service_url("transfer", environment="production")
        == "https://transfer.api.globus.org/"
    )
    assert (
        globus_sdk.config.get_service_url("auth", environment="preview")
        == "https://auth.preview.globus.org/"
    )
    assert (
        globus_sdk.config.get_service_url("search", environment="preview")
        == "https://search.api.preview.globus.org/"
    )
    assert (
        globus_sdk.config.get_service_url("timer", environment="preview")
        == "https://preview.timer.automate.globus.org/"
    )

    with pytest.raises(ValueError):
        globus_sdk.config.get_service_url("auth", environment="nonexistent")


ca_bundle_file = pathlib.Path(__file__).parent.absolute() / "CA-Bundle.cert"
ca_bundle_directory = pathlib.Path(__file__).parent.absolute()
ca_bundle_non_existent = pathlib.Path(__file__).parent.absolute() / "bogus.bogus"


@pytest.mark.parametrize(
    "value, expected_result",
    [(x, True) for x in ["1", "YES", "true", "t", "True", "ON"]]
    + [(x, False) for x in ["0", "NO", "false", "f", "False", "OFF"]]
    + [(str(ca_bundle_file), str(ca_bundle_file))]
    + [
        ("invalid", ValueError),
        ("1.0", ValueError),
        ("0.0", ValueError),
        (str(ca_bundle_directory), ValueError),
        (str(ca_bundle_non_existent), ValueError),
    ],
)
def test_get_ssl_verify(value, expected_result, monkeypatch):
    """
    Confirms bool cast returns correct bools from sets of string values
    """
    monkeypatch.setenv("GLOBUS_SDK_VERIFY_SSL", value)
    if expected_result is not ValueError:
        assert globus_sdk.config.get_ssl_verify() == expected_result
    else:
        with pytest.raises(expected_result):
            globus_sdk.config.get_ssl_verify()


@pytest.mark.parametrize(
    "value",
    [
        "invalid",
        1.0,
        object(),
        ca_bundle_directory,
        str(ca_bundle_directory),
        ca_bundle_non_existent,
        str(ca_bundle_non_existent),
    ],
)
def test_get_ssl_verify_rejects_bad_explicit_value(value, monkeypatch):
    monkeypatch.delenv("GLOBUS_SDK_VERIFY_SSL", raising=False)
    with pytest.raises(ValueError):
        globus_sdk.config.get_ssl_verify(value)


def test_get_ssl_verify_with_explicit_value():
    with mock.patch.dict(os.environ):
        os.environ["GLOBUS_SDK_VERIFY_SSL"] = "false"
        assert globus_sdk.config.get_ssl_verify(True) is True
        assert globus_sdk.config.get_ssl_verify(False) is False
        assert globus_sdk.config.get_ssl_verify(ca_bundle_file) == str(ca_bundle_file)
        assert globus_sdk.config.get_ssl_verify(str(ca_bundle_file)) == str(
            ca_bundle_file
        )
        os.environ["GLOBUS_SDK_VERIFY_SSL"] = "on"
        assert globus_sdk.config.get_ssl_verify(True) is True
        assert globus_sdk.config.get_ssl_verify(False) is False
        assert globus_sdk.config.get_ssl_verify(str(ca_bundle_file)) == str(
            ca_bundle_file
        )


@pytest.mark.parametrize(
    "value, expected_result",
    [(x, 1.0) for x in ["1.0", "1", " 1", "1.0  "]]
    + [(x, 0.0) for x in ["0", "0.0"]]
    + [("", 60.0)]
    + [("-1", None)]  # type: ignore
    + [(x, ValueError) for x in ["invalid", "no", "1.1.", "t", "f"]],  # type: ignore
)
def test_get_http_timeout(value, expected_result):
    """
    Confirms bool cast returns correct bools from sets of string values
    """
    with mock.patch.dict(os.environ):
        os.environ["GLOBUS_SDK_HTTP_TIMEOUT"] = value
        if expected_result is None or isinstance(expected_result, float):
            assert globus_sdk.config.get_http_timeout() == expected_result
        else:
            with pytest.raises(expected_result):
                globus_sdk.config.get_http_timeout()


def test_get_http_timeout_with_explicit_value():
    with mock.patch.dict(os.environ):
        os.environ["GLOBUS_SDK_HTTP_TIMEOUT"] = "120"
        assert globus_sdk.config.get_http_timeout(10) == 10.0
        assert globus_sdk.config.get_http_timeout(0) == 0.0
        del os.environ["GLOBUS_SDK_HTTP_TIMEOUT"]
        assert globus_sdk.config.get_http_timeout(60) == 60.0


def test_get_environment_name():
    with mock.patch.dict(os.environ):
        # set an environment value, ensure that it's returned
        os.environ["GLOBUS_SDK_ENVIRONMENT"] = "beta"
        assert globus_sdk.config.get_environment_name() == "beta"

        # clear that value, "production" should be returned
        del os.environ["GLOBUS_SDK_ENVIRONMENT"]
        assert globus_sdk.config.get_environment_name() == "production"

        # ensure that passing a value returns that value
        assert globus_sdk.config.get_environment_name("beta") == "beta"


def test_env_config_registration():
    with mock.patch.dict(globus_sdk.config.EnvConfig._registry):
        # should be None, we don't have an environment named 'moon'
        assert globus_sdk.config.EnvConfig.get_by_name("moon") is None

        # now, create the moon
        class MoonEnvConfig(globus_sdk.config.EnvConfig):
            envname = "moon"
            domain = "apollo.globus.org"

        # a lookup by "moon" should now get this config object
        assert globus_sdk.config.EnvConfig.get_by_name("moon") is MoonEnvConfig


def test_service_url_overrides():
    with mock.patch.dict(globus_sdk.config.EnvConfig._registry):

        class MarsEnvConfig(globus_sdk.config.EnvConfig):
            envname = "mars"
            domain = "mars.globus.org"
            auth_url = "https://perseverance.mars.globus.org/"

        # this one was customized
        assert (
            MarsEnvConfig.get_service_url("auth")
            == "https://perseverance.mars.globus.org/"
        )
        # but this one was not
        assert (
            MarsEnvConfig.get_service_url("search")
            == "https://search.api.mars.globus.org/"
        )


def test_service_url_from_env_var():
    with mock.patch.dict(os.environ):
        os.environ["GLOBUS_SDK_SERVICE_URL_TRANSFER"] = "https://transfer.example.org/"
        # environment setting gets ignored at this point -- only the override applies
        assert (
            globus_sdk.config.get_service_url("transfer", environment="preview")
            == "https://transfer.example.org/"
        )
        assert (
            globus_sdk.config.get_service_url("transfer", environment="production")
            == "https://transfer.example.org/"
        )
        # also try with a made up service
        os.environ["GLOBUS_SDK_SERVICE_URL_ION_CANNON"] = (
            "https://ion-cannon.example.org/"
        )
        assert (
            globus_sdk.config.get_service_url("ion_cannon", environment="production")
            == "https://ion-cannon.example.org/"
        )

        for env in ["sandbox", "test", "integration"]:
            os.environ["GLOBUS_SDK_ENVIRONMENT"] = env
            assert (
                globus_sdk.config.get_service_url("auth")
                == f"https://auth.{env}.globuscs.info/"
            )
            assert (
                globus_sdk.config.get_webapp_url()
                == f"https://app.{env}.globuscs.info/"
            )
