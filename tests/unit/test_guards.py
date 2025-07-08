import uuid

import pytest

from globus_sdk import exc
from globus_sdk._internal import guards
from globus_sdk._internal.serializable import Serializable


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
    assert guards.is_list_of(value, typ) == ok


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
    assert guards.is_optional(value, typ) == ok


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
    assert guards.is_optional_list_of(value, typ) == ok


@pytest.mark.parametrize("value", (uuid.UUID(int=0), str(uuid.UUID(int=1))))
def test_uuidlike_ok(value):
    assert guards.validators.uuidlike("foo", value) == value


@pytest.mark.parametrize("value", (str(uuid.UUID(int=0))[:-1], ""))
def test_uuidlike_fails_value(value):
    with pytest.raises(
        exc.ValidationError, match="'foo' must be a valid UUID"
    ) as excinfo:
        guards.validators.uuidlike("foo", value)

    err = excinfo.value
    assert f"value='{value}'" in str(err)


@pytest.mark.parametrize("value", (object(), None, ["bar"]))
def test_uuidlike_fails_type(value):
    with pytest.raises(
        exc.ValidationError, match="'foo' must be a UUID or str"
    ) as excinfo:
        guards.validators.uuidlike("foo", value)

    err = excinfo.value
    assert f"value='{value}'" in str(err)


@pytest.mark.parametrize(
    "validator, value",
    (
        pytest.param(guards.validators.str_, "bar", id="str"),
        pytest.param(guards.validators.int_, 0, id="int-0"),
        pytest.param(guards.validators.int_, 1, id="int-1"),
        pytest.param(guards.validators.opt_str, "bar", id="opt_str-str"),
        pytest.param(guards.validators.opt_str, None, id="opt_str-None"),
        pytest.param(guards.validators.opt_bool, True, id="opt_bool-True"),
        pytest.param(guards.validators.opt_bool, False, id="opt_bool-False"),
        pytest.param(guards.validators.opt_bool, None, id="opt_bool-None"),
        pytest.param(guards.validators.str_list, [], id="str_list-empty"),
        pytest.param(guards.validators.str_list, ["foo"], id="str_list-onestr"),
        pytest.param(guards.validators.opt_str_list, [], id="opt_str_list-empty"),
        pytest.param(guards.validators.opt_str_list, ["foo"], id="opt_str_list-onestr"),
        pytest.param(guards.validators.opt_str_list, None, id="opt_str_list-None"),
        pytest.param(
            guards.validators.opt_str_list_or_commasep,
            [],
            id="opt_str_list_or_commasep-emptylist",
        ),
        pytest.param(
            guards.validators.opt_str_list_or_commasep,
            ["foo"],
            id="opt_str_list_or_commasep-list",
        ),
        pytest.param(
            guards.validators.opt_str_list_or_commasep,
            None,
            id="opt_str_list_or_commasep-None",
        ),
    ),
)
def test_simple_validator_passing(validator, value):
    assert validator("foo", value) == value


@pytest.mark.parametrize(
    "validator, value, match_message",
    (
        pytest.param(guards.validators.str_, 1, "'foo' must be a string", id="str-int"),
        pytest.param(
            guards.validators.str_, False, "'foo' must be a string", id="str-bool"
        ),
        pytest.param(
            guards.validators.str_, None, "'foo' must be a string", id="str-None"
        ),
        pytest.param(
            guards.validators.int_, "bar", "'foo' must be an int", id="int-str"
        ),
        pytest.param(
            guards.validators.opt_str,
            0,
            "'foo' must be a string or null",
            id="opt_str-int",
        ),
        pytest.param(
            guards.validators.opt_bool,
            0,
            "'foo' must be a bool or null",
            id="opt_bool-int",
        ),
        pytest.param(
            guards.validators.str_list,
            "x",
            "'foo' must be a list of strings",
            id="str_list-str",
        ),
        pytest.param(
            guards.validators.opt_str_list,
            "x",
            "'foo' must be a list of strings or null",
            id="opt_str_list-str",
        ),
        pytest.param(
            guards.validators.opt_str_list_or_commasep,
            0,
            "'foo' must be a list of strings or a comma-delimited string or null",
            id="opt_str_list_or_commasep-int",
        ),
    ),
)
def test_simple_validator_failing(validator, value, match_message):
    with pytest.raises(exc.ValidationError, match=match_message):
        validator("foo", value)


def test_instance_or_dict_validator_failing():
    class MyObj(Serializable):
        def __init__(self, *, extra=None) -> None:
            pass

    with pytest.raises(
        exc.ValidationError, match="'foo' must be a 'MyObj' object or a dictionary"
    ):
        guards.validators.instance_or_dict("foo", object(), MyObj)


def test_instance_or_dict_validator_pass_on_simple_instance():
    class MyObj(Serializable):
        def __init__(self, *, extra=None) -> None:
            pass

    x = MyObj()
    y = guards.validators.instance_or_dict("foo", x, MyObj)
    assert x is y


def test_instance_or_dict_validator_pass_on_simple_dict():
    class MyObj(Serializable):
        def __init__(self, *, extra=None) -> None:
            pass

    x = guards.validators.instance_or_dict("foo", {}, MyObj)
    assert isinstance(x, MyObj)


def test_strlist_or_commasep_splits_str():
    x = guards.validators.opt_str_list_or_commasep("foo", "foo,bar,baz")
    assert x == ["foo", "bar", "baz"]
