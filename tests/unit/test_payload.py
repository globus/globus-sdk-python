from __future__ import annotations

import typing as t

import attrs
import pytest

from globus_sdk import payload, utils
from globus_sdk.transport import JSONRequestEncoder


def _serialize(obj: payload.Payload):
    encoder = JSONRequestEncoder()
    return encoder._prepare_data(obj)


def test_simple_payload_class_serialization():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: str
        bar: int

    doc = _serialize(MyPayloadType(foo="foo", bar=1))
    assert doc == {"foo": "foo", "bar": 1}


def test_simple_payload_class_serialization_with_extra():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: str
        bar: int

    doc = _serialize(MyPayloadType(foo="foo", bar=1, extra={"baz": "baz"}))
    assert doc == {"foo": "foo", "bar": 1, "baz": "baz"}


@pytest.mark.parametrize(
    "input_value, expected",
    (
        (["bar"], ["bar"]),
        (("bar", "baz"), ["bar", "baz"]),
        ("bar", ["bar"]),
        (range(3), ["0", "1", "2"]),
    ),
)
def test_payload_strlist_field(input_value, expected):
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: t.Iterable[str] | utils.MissingType = attrs.field(
            default=utils.MISSING,
            converter=payload.converters.str_list,
        )

    # works via init
    doc = _serialize(MyPayloadType(foo=input_value))
    assert doc == {"foo": expected}

    # works via setattr
    p = MyPayloadType()
    p.foo = input_value
    assert _serialize(p) == {"foo": expected}


@pytest.mark.parametrize(
    "input_value, expected",
    (
        (None, None),
        (("bar", "baz"), ["bar", "baz"]),
        ("bar", ["bar"]),
        (range(3), ["0", "1", "2"]),
    ),
)
def test_payload_nullable_strlist_field(input_value, expected):
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: t.Iterable[str] | None | utils.MissingType = attrs.field(
            default=utils.MISSING,
            converter=payload.converters.nullable_str_list,
        )

    # works via init
    doc = _serialize(MyPayloadType(foo=input_value))
    assert doc == {"foo": expected}

    # works via setattr
    p = MyPayloadType()
    p.foo = input_value
    assert _serialize(p) == {"foo": expected}


def test_encoder_recursively_serializes_payloads():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: str
        bar: int

    @attrs.define
    class MyPayloadType2(payload.Payload):
        baz: MyPayloadType

    doc = _serialize(MyPayloadType2(baz=MyPayloadType(foo="foo", bar=1)))
    assert doc == {"baz": {"foo": "foo", "bar": 1}}


def test_extra_emits_warnings_when_aligned_with_fields_but_acts_as_override():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: str

    with pytest.warns(
        RuntimeWarning,
        match="'extra' keys overlap with defined fields.+redundant_fields={'foo'}",
    ):
        x = MyPayloadType(foo="foo", extra={"foo": "bar"})
    doc = _serialize(x)
    assert doc == {"foo": "bar"}


def test_non_nullable_list_converter_fails_on_none():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: t.Iterable[dict] = attrs.field(converter=payload.converters.list_)

    with pytest.raises(TypeError):
        MyPayloadType(foo=None)


def test_nullable_list_converter_allows_none():
    @attrs.define
    class MyPayloadType(payload.Payload):
        foo: t.Iterable[dict] = attrs.field(converter=payload.converters.nullable_list)

    doc = _serialize(MyPayloadType(foo=None))
    assert doc == {"foo": None}
