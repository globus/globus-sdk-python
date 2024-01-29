# test behaviors of the globus_sdk.payload usage of dataclasses

import typing as t

import attrs

from globus_sdk import payload, utils

my_str: str
my_int: int
my_optstr: str | None


@attrs.define
class MyPayloadType1(payload.Payload):
    foo: str
    bar: int


doc1 = MyPayloadType1(foo="foo", bar=1)
my_str = doc1.foo
my_int = doc1.bar
my_optstr = doc1.foo
my_str = doc1.bar  # type: ignore[assignment]
my_int = doc1.foo  # type: ignore[assignment]

doc1_extra = MyPayloadType1(foo="foo", bar=1, extra={"extra": "somedata"})


@attrs.define
class MyPayloadType2(payload.Payload):
    foo: str | utils.MissingType = attrs.field(default=utils.MISSING)


doc2 = MyPayloadType2()
my_str = doc2.foo  # type: ignore[assignment]
my_missingstr: str | utils.MissingType = doc2.foo


@attrs.define
class MyPayloadType3(payload.Payload):
    foo: t.Iterable[str] | utils.MissingType = attrs.field(
        default=utils.MISSING, converter=payload.converters.str_list
    )


doc3 = MyPayloadType3(str(i) for i in range(3))
assert not isinstance(doc3.foo, utils.MissingType)
# in spite of the application of the converter, the type is not narrowed from the
# annotated type (Iterable[str]) to the converted type (list[str])
#
# this is a limitations in mypy; see:
#   https://github.com/python/mypy/issues/3004
#
# it *may* be resolved when `dataclasses` adds support for converters and mypy supports
# that usage, as the `attrs` plugin could use the dataclass converter support path
my_str = doc3.foo[0]  # type: ignore[index]
t.assert_type(doc3.foo, t.Iterable[str])
