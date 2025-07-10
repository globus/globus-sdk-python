import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.token_storage.v2.base import _slugify_app_name


@pytest.mark.parametrize(
    "app_name, expected_slug",
    (
        ("Globus CLI v3.30.0", "globus-cli-v3-30-0"),
        ("my-cool-app", "my-cool-app"),
        ("jonathan", "jonathan"),
    ),
)
def test_app_name_slugification_of_basic_app_names(app_name, expected_slug):
    actual_slug = _slugify_app_name(app_name)
    assert actual_slug == expected_slug


def test_app_name_slugification_replaces_reserved_characters():
    app_name = 'glob<>:"/\\|?*us'
    expected = "glob+++++++++us"
    actual_slug = _slugify_app_name(app_name)
    assert actual_slug == expected


def test_app_name_slugification_removes_control_characters():
    app_name = "glob\0\n\t\rus"
    expected = "globus"
    actual_slug = _slugify_app_name(app_name)
    assert actual_slug == expected


def test_app_name_slugification_rejects_empty_name():
    with pytest.raises(GlobusSDKUsageError, match="name results in the empty string"):
        _slugify_app_name("\n\t\r")


@pytest.mark.parametrize("app_name", ("CON", "PRN\n", "nul", "LPT9", "COM1"))
def test_app_name_slugification_rejects_reserved_names(app_name):
    # # https://stackoverflow.com/a/31976060
    with pytest.raises(GlobusSDKUsageError, match="reserved filename"):
        _slugify_app_name(app_name)


def test_app_name_allows_reserved_name_prefixes():
    # Prefix of app name ("CON") is reserved, but the slugified name is not.
    app_name = "Continuous Deployment App"
    expected = "continuous-deployment-app"
    actual_slug = _slugify_app_name(app_name)
    assert actual_slug == expected
