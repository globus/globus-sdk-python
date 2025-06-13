"""
WARNING: for internal use only.
Everything in SDK private modules is meant to be internal only, but that
holds for this module **in particular**.

Usage:

    from globus_sdk._classproperty import classproperty

    class A:
        @classproperty
        def foo(self_or_cls): ...
"""

from __future__ import annotations

import os
import sys
import typing as t

T = t.TypeVar("T")
R = t.TypeVar("R")


def _in_sphinx_build() -> bool:  # pragma: no cover
    # check if `sphinx-build` was used to invoke
    return os.path.basename(sys.argv[0]) in ["sphinx-build", "sphinx-build.exe"]


class _classproperty(t.Generic[T, R]):
    """
    A hybrid class/instance property descriptor.

    On a class, the decorated method will be invoked with `cls`.
    On an instance, the decorated method will be invoked with `self`.
    """

    def __init__(self, func: t.Callable[[type[T] | T], R]) -> None:
        self.func = func

    def __get__(self, obj: T | None, cls: type[T]) -> R:
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
if _in_sphinx_build():  # pragma: no cover

    def classproperty(func: t.Callable[[T | type[T]], R]) -> _classproperty[T, R]:
        # type ignore this because
        # - it doesn't match the return type
        # - mypy doesn't understand classmethod(property(...)) on older pythons
        return classmethod(property(func))  # type: ignore

else:

    def classproperty(func: t.Callable[[T | type[T]], R]) -> _classproperty[T, R]:
        return _classproperty(func)
