from __future__ import annotations

import abc
import sys
import typing as t

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# TODO: Remove this dispatch after we drop Python 3.8 support.
#       In 3.9+ `dict.__class_getitem__` is available.
if t.TYPE_CHECKING:
    # pylint: disable=unsubscriptable-object
    _PayloadBaseDict = t.Dict[str, t.Any]
else:
    _PayloadBaseDict = dict


class Payload(_PayloadBaseDict):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload.

    Payload types inheriting from this class can be passed directly to the client
    ``post()``, ``put()``, and ``patch()`` methods. These methods will
    recognize a ``PayloadBase`` and apply conversions for serialization with
    the requested encoder (e.g. as a JSON request body).
    """


class AbstractPayload(Payload, abc.ABC):
    """
    An abstract class which is a Payload.

    This is a shim which is needed because we have a metaclass conflict between
    dict:type and ABC:ABCMeta.

    Setting the metaclass helps type checkers understand that such classes are
    abstract.
    """

    # explicitly define `__new__` in order to check for abstract methods which
    # were not redefined
    def __new__(cls, *args: t.Any, **kwargs: t.Any) -> Self:
        obj = super().__new__(cls, *args, **kwargs)
        abstractmethods: frozenset[str] = (
            obj.__abstractmethods__  # type: ignore[attr-defined]
        )
        if abstractmethods:
            s = "" if len(abstractmethods) == 1 else "s"
            methodnames = ", ".join(f"'{f}'" for f in abstractmethods)
            # this error very closely imitates the errors produced by ABCMeta
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} without "
                f"an implementation for abstract method{s} {methodnames}"
            )
        return obj
