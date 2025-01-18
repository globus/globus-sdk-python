import textwrap
import uuid

import pytest

from globus_sdk import utils


def test_b64str_non_ascii():
    test_string = "ⓤⓢⓔⓡⓝⓐⓜⓔ"
    expected_b64 = "4pOk4pOi4pOU4pOh4pOd4pOQ4pOc4pOU"

    assert utils.b64str(test_string) == expected_b64


def test_b64str_ascii():
    test_string = "username"
    expected_b64 = "dXNlcm5hbWU="

    assert utils.b64str(test_string) == expected_b64


def test_sha256string():
    test_string = "foo"
    expected_sha = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"

    assert utils.sha256_string(test_string) == expected_sha


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
    assert utils.get_nice_hostname() == result


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
    assert utils.slash_join(a, b) == "a/b"


def test_payload_wrapper_methods():
    # just make sure that PayloadWrapper acts like a dict...
    data = utils.PayloadWrapper()
    assert "foo" not in data
    with pytest.raises(KeyError):
        data["foo"]
    data["foo"] = 1
    assert "foo" in data
    assert data["foo"] == 1
    del data["foo"]
    assert "foo" not in data
    assert len(data) == 0
    assert list(data) == []
    data["foo"] = 1
    data["bar"] = 2
    assert len(data) == 2
    assert data.data == {"foo": 1, "bar": 2}
    data.update({"x": "hello", "y": "world"})
    assert data.data == {"foo": 1, "bar": 2, "x": "hello", "y": "world"}


def test_classproperty_simple():
    class Foo:
        x = {"x": 1}

        @utils.classproperty
        def y(self_or_cls):
            return self_or_cls.x["x"]

    assert Foo.y == 1


def test_classproperty_prefers_instance():
    class Foo:
        x = {"x": 1}

        def __init__(self) -> None:
            self.x = {"x": 2}

        @utils.classproperty
        def y(self_or_cls):
            return self_or_cls.x["x"]

    assert Foo.y == 1
    assert Foo().y == 2


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["foo"]),
        ((1, 2, 3), ["1", "2", "3"]),
        (uuid.UUID(int=10), [f"{uuid.UUID(int=10)}"]),
        (["foo", uuid.UUID(int=5)], ["foo", f"{uuid.UUID(int=5)}"]),
    ),
)
def test_safe_strseq_iter(value, expected_result):
    assert list(utils.safe_strseq_iter(value)) == expected_result


def test_read_sphinx_params():
    docstring = """
    preamble

    :param param1: some doc on one line
    :param param2: other doc
        spanning multiple lines
    :param param3: a doc
        spanning
        many
        lines
    :param param4: a doc
        spanning lines

        with a break in the middle ^
    :param param5: another


    :param param6: and a final one after some whitespace

    epilogue
    """
    params = utils.read_sphinx_params(docstring)
    assert len(params) == 6
    assert params[0] == ":param param1: some doc on one line"
    assert params[1] == ":param param2: other doc\n    spanning multiple lines"
    assert params[2] == textwrap.dedent(
        """\
        :param param3: a doc
            spanning
            many
            lines"""
    )
    assert params[3] == textwrap.dedent(
        """\
        :param param4: a doc
            spanning lines

            with a break in the middle ^"""
    )
    assert params[4] == ":param param5: another"
    assert params[5] == ":param param6: and a final one after some whitespace"

    # clear the cache after the test
    # not essential, but reduces the risk that this impacts some future test
    utils.read_sphinx_params.cache_clear()
