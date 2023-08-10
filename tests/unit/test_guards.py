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
