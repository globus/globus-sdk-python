import pytest

from globus_sdk._internal.utils import get_nice_hostname, sha256_string, slash_join


def test_sha256string():
    test_string = "foo"
    expected_sha = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"

    assert sha256_string(test_string) == expected_sha


@pytest.mark.parametrize(
    "platform_value, result",
    (
        # platform.node() can return '' when it doesn't know the hostname
        # turn this into None
        pytest.param("", None, id="empty-is-none"),
        # macOS adds '.local' to the user's chosen machine name
        pytest.param(
            "VeryCoolMacbook.local", "VeryCoolMacbook", id="remove-local-suffix"
        ),
        # the "boring" case is when we do no extra work
        pytest.param("linux-workstation", "linux-workstation", id="boring"),
    ),
)
def test_get_nice_hostname(platform_value, result, monkeypatch):
    monkeypatch.setattr("platform.node", lambda: platform_value)
    assert get_nice_hostname() == result


@pytest.mark.parametrize(
    "a, b",
    [(a, b) for a in ["a", "a/"] for b in ["b", "/b"]]
    + [("a/b", c) for c in ["", None]],  # type: ignore
)
def test_slash_join(a, b):
    """
    slash_joins a's with and without trailing "/"
    to b's with and without leading "/"
    Confirms all have the same correct slash_join output
    """
    assert slash_join(a, b) == "a/b"
