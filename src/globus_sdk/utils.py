from __future__ import annotations

import collections
import collections.abc
import hashlib
import os
import sys
import typing as t
import uuid
from base64 import b64encode
from enum import Enum

T = t.TypeVar("T")
R = t.TypeVar("R")

if t.TYPE_CHECKING:
    # pylint: disable=unsubscriptable-object
    PayloadWrapperBase = collections.UserDict[str, t.Any]
else:
    PayloadWrapperBase = collections.UserDict


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def b64str(s: str) -> str:
    return b64encode(s.encode("utf-8")).decode("utf-8")


def slash_join(a: str, b: str | None) -> str:
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
    """
    if not b:  # "" or None, don't append a slash
        return a
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b


def safe_strseq_iter(
    value: t.Iterable[t.Any] | str | uuid.UUID,
) -> t.Iterator[str]:
    """
    Given an Iterable (typically of strings), produce an iterator over it of strings.
    This is a passthrough with some caveats:
    - if the value is a solitary string, yield only that value
    - if the value is a solitary UUID, yield only that value (as a string)
    - str values in the iterable which are not strings

    This helps handle cases where a string is passed to a function expecting an iterable
    of strings, as well as cases where an iterable of UUID objects is accepted for a
    list of IDs, or something similar.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, uuid.UUID):
        yield str(value)
    else:
        for x in value:
            yield str(x)


def render_enums_for_api(value: t.Any) -> t.Any:
    """
    Convert enum values to their underlying value.

    If a value is an iterable type, it will be converted to a list and the values will
    also be converted if they are enum values.
    """
    # special-case: handle str and bytes because these types are technically iterable
    # types (of bytes or str values) which could trip someone up
    if isinstance(value, (str, bytes)):
        return value
    if isinstance(value, collections.abc.Iterable):
        return [render_enums_for_api(x) for x in value]
    return value.value if isinstance(value, Enum) else value


class PayloadWrapper(PayloadWrapperBase):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload, e.g. as JSON.

    Payload types inheriting from this class can be passed directly to the client
    ``post()``, ``put()``, and ``patch()`` methods instead of a dict. These methods will
    recognize a ``PayloadWrapper`` and convert it to a dict for serialization with the
    requested encoder (e.g. as a JSON request body).
    """

    # use UserDict rather than subclassing dict so that our API is always consistent
    # e.g. `dict.pop` does not invoke `dict.__delitem__`. Overriding `__delitem__` on a
    # dict subclass can lead to inconsistent behavior between usages like these:
    #   x = d["k"]; del d["k"]
    #   x = d.pop("k")
    #
    # UserDict inherits from MutableMapping and only defines the dunder methods, so
    # changing its behavior safely/consistently is simpler

    #
    # internal helpers for setting non-null values
    #

    def _set_value(
        self,
        key: str,
        val: t.Any,
        callback: t.Callable[[t.Any], t.Any] | None = None,
    ) -> None:
        if val is not None:
            self[key] = callback(val) if callback else val

    def _set_optstrs(self, **kwargs: t.Any) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=str)

    def _set_optstrlists(self, **kwargs: t.Iterable[t.Any] | None) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=lambda x: list(safe_strseq_iter(x)))

    def _set_optbools(self, **kwargs: bool | None) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=bool)

    def _set_optints(self, **kwargs: t.Any) -> None:
        for k, v in kwargs.items():
            self._set_value(k, v, callback=int)


def in_sphinx_build() -> bool:  # pragma: no cover
    # check if `sphinx-build` was used to invoke
    return os.path.basename(sys.argv[0]) in ["sphinx-build", "sphinx-build.exe"]


class _classproperty(t.Generic[T, R]):
    """
    WARNING: for internal use only.
    Everything in `globus_sdk.utils` is meant to be internal only, but that holds
    for this class **in particular**.

    This is a well-typed Generic Descriptor which can be used to wrap decorated
    functions. Usage should be:

        @utils.classproperty
        def foo(self_or_cls): ...

    Note that this descriptor will pass an instance (self) if possible, and the
    class (cls) only if there is no instance. This is unlike ``classmethod``.

    For more guidance on how this works, see the python3 descriptor guide:
      https://docs.python.org/3/howto/descriptor.html#properties
    """

    def __init__(self, func: t.Callable[[type[T]], R]) -> None:
        self.func = func

    def __get__(self, obj: t.Any, cls: type[T]) -> R:
        # NOTE: our __get__ here prefers the object over the class when possible
        # although well-defined behavior for a descriptor, this contradicts the
        # expectation that developers may have from `classmethod`
        if obj is None:
            return self.func(cls)
        return self.func(obj)


# if running under sphinx, define this as the stacked classmethod(property(...))
# decoration, so that proper autodoc generation happens
# this is based on the python3.9 behavior which supported stacking these decorators
# however, that support was pulled in 3.10 and is not going to be reintroduced at
# present
# therefore, this sphinx behavior may not be stable in the long term
if in_sphinx_build():  # pragma: no cover

    def classproperty(func: t.Callable[[T], R]) -> _classproperty[T, R]:
        # type ignore this because
        # - it doesn't match the return type
        # - mypy doesn't understand classmethod(property(...)) on older pythons
        return classmethod(property(func))  # type: ignore

else:

    def classproperty(func: t.Callable[[T], R]) -> _classproperty[T, R]:
        # type cast to convert instance method to class method
        return _classproperty(t.cast(t.Callable[[t.Type[T]], R], func))
