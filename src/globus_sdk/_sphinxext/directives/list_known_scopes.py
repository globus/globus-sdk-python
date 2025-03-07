from __future__ import annotations

import typing as t
from pydoc import locate

from docutils.parsers.rst import directives

from globus_sdk.scopes import ScopeBuilder

from .add_content_directive import AddContentDirective


class ListKnownScopes(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "example_scope": directives.unchanged,
        # Allow overriding the base name to match how the ScopeBuilder will be accessed.
        "base_name": directives.unchanged,
    }

    def gen_rst(self) -> t.Iterator[str]:
        sb_name = self.arguments[0]
        sb_basename = sb_name.split(".")[-1]
        if "base_name" in self.options:
            sb_basename = self.options["base_name"]

        example_scope = None
        if "example_scope" in self.options:
            example_scope = self.options["example_scope"].strip()
        known_scopes = extract_known_scopes(sb_name)
        if example_scope is None:
            example_scope = known_scopes[0]

        yield ""
        yield "Various scopes are available as attributes of this object."
        yield f"For example, access the ``{example_scope}`` scope with"
        yield ""
        yield f">>> {sb_basename}.{example_scope}"
        yield ""
        yield "**Supported Scopes**"
        yield ""
        for s in known_scopes:
            yield f"* ``{s}``"
        yield ""
        yield ""


def extract_known_scopes(scope_builder_name: str) -> list[str]:
    sb = locate(scope_builder_name)
    if not isinstance(sb, ScopeBuilder):
        raise RuntimeError(
            f"Expected {sb} to be a ScopeBuilder, but got {type(sb)} instead"
        )
    return sb.scope_names
