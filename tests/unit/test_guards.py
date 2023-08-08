import pytest

from globus_sdk import _guards


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        ([], str, True),
        ([1, 2], int, True),
        (["1", ""], str, True),
        ([], list, True),
        ([[], [1, 2], ["foo"]], list, True),
        # failing
        ([1], str, False),
        (["foo"], int, False),
        ((1, 2), int, False),
        (list, list, False),
        (list, str, False),
        (["foo", 1], str, False),
        ([1, 2], list, False),
    ],
)
def test_list_of_guard(value, typ, ok):
    assert _guards.is_list_of(value, typ) == ok


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        (None, str, True),
        ("foo", str, True),
        # failing
        (b"foo", str, False),
        ("", int, False),
        (type(None), str, False),
    ],
)
def test_opt_guard(value, typ, ok):
    assert _guards.is_optional(value, typ) == ok


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        ([], str, True),
        ([], int, True),
        ([1, 2], int, True),
        (["1", ""], str, True),
        (None, str, True),
        # failing
        # NB: the guard checks `list[str] | None`, not `list[str | None]`
        ([None], str, False),
        (b"foo", str, False),
        ("", str, False),
        (type(None), str, False),
    ],
)
def test_opt_list_guard(value, typ, ok):
    assert _guards.is_optional_list_of(value, typ) == ok


def test_reduced_guards():
    reduced_str = _guards.reduce(str)

    # apply => isinstance
    assert reduced_str.apply("foo")
    assert not reduced_str.apply(None)

    # list_of => is_list_of
    assert reduced_str.list_of(["foo", "bar"])
    assert not reduced_str.list_of(["foo", "bar", 1])

    # optional => is_optional
    assert reduced_str.optional("foo")
    assert reduced_str.optional(None)
    assert not reduced_str.optional(1)

    # optional_list => is_optional_list_of
    assert reduced_str.optional_list(["foo", "bar"])
    assert not reduced_str.optional_list(["foo", "bar", 1])
    assert reduced_str.optional_list(None)
    assert not reduced_str.optional_list("")
