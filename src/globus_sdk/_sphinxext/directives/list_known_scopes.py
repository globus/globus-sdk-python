from __future__ import annotations

import typing as t
from pydoc import locate

from docutils.parsers.rst import directives

from globus_sdk.scopes import Scope, ScopeCollection

from .add_content_directive import AddContentDirective


class ListKnownScopes(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "example_scope": directives.unchanged,
        # Allow overriding the base name to match how the ScopeCollection will
        # be accessed.
        "base_name": directives.unchanged,
    }

    def gen_rst(self) -> t.Iterator[str]:
        sc_name = self.arguments[0]
        sc_basename = sc_name.split(".")[-1]
        if "base_name" in self.options:
            sc_basename = self.options["base_name"]

        example_scope = None
        if "example_scope" in self.options:
            example_scope = self.options["example_scope"].strip()
        known_scopes = extract_known_scopes(sc_name)
        if example_scope is None:
            example_scope = known_scopes[0]

        yield ""
        yield "Various scopes are available as attributes of this object."
        yield f"For example, access the ``{example_scope}`` scope with"
        yield ""
        yield f">>> {sc_basename}.{example_scope}"
        yield ""
        yield "**Supported Scopes**"
        yield ""
        for s in known_scopes:
            yield f"* ``{s}``"
        yield ""
        yield ""


def extract_known_scopes(scope_collection_name: str) -> list[str]:
    sc = locate(scope_collection_name)
    if isinstance(sc, ScopeCollection):
        return [name for name in dir(sc) if isinstance(getattr(sc, name), Scope)]

    raise RuntimeError(
        f"Expected {sc} to be a scope collection, but got {type(sc)} instead"
    )
