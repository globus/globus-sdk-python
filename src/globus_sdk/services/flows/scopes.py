from __future__ import annotations

import typing as t

from globus_sdk.scopes import ScopeBuilder


class SpecificFlowScopesClassStub(ScopeBuilder):
    """
    This stub object ensures that the type deductions for type checkers (e.g. mypy) on
    SpecificFlowClient.scopes are correct.

    Primarily, it should be possible to access the `scopes` attribute, the `user`
    scope, and the `resource_server`, but these usages should raise specific and
    informative runtime errors.

    Our types are therefore less accurate for class-var access, but more accurate for
    instance-var access.
    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__("<stub>")

    def __getattr__(self, name: str) -> t.Any:
        if name == "user":
            _raise_attr_error("scopes")
        elif name == "resource_server":
            _raise_attr_error("resource_server")
        return super().__getattr__(name)

    def __getattribute__(self, name: str) -> t.Any:
        if name == "resource_server":
            _raise_attr_error("resource_server")
        return object.__getattribute__(self, name)


def _raise_attr_error(name: str) -> t.NoReturn:
    raise AttributeError(
        f"It is not valid to attempt to access the {name} of the "
        "SpecificFlowClient class. "
        f"Instead, instantiate a SpecificFlowClient and access the {name} "
        "from that instance."
    )
