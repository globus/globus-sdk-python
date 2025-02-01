"""
A Globus SDK Sphinx Extension for Autodoc of Class Methods
"""

from __future__ import annotations

from .autodoc_hooks import after_autodoc_signature_replace_MISSING_repr
from .custom_directives import (
    AddContentDirective,
    AutoMethodList,
    EnumerateTestingFixtures,
    ExpandTestingFixture,
    ExternalDocLink,
    ListKnownScopes,
    PaginatedUsage,
)
from .roles import extdoclink_role


class CopyParams(AddContentDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 0

    def gen_rst(self):
        import globus_sdk

        source_object_name: str = self.arguments[0]
        path = source_object_name.split(".")

        # traverse `globus_sdk` element by element to find the target
        source_object = globus_sdk
        for element in path:
            source_object = getattr(source_object, element)

        if self.content:
            content = iter(self.content)
        else:
            content = ()

        for line in content:
            if line.strip() == "<YIELD>":
                break
            yield line

        yield from globus_sdk.utils.read_sphinx_params(source_object.__doc__)

        for line in content:
            yield line


def setup(app):
    app.add_directive("automethodlist", AutoMethodList)
    app.add_directive("listknownscopes", ListKnownScopes)
    app.add_directive("enumeratetestingfixtures", EnumerateTestingFixtures)
    app.add_directive("expandtestfixture", ExpandTestingFixture)
    app.add_directive("extdoclink", ExternalDocLink)
    app.add_directive("paginatedusage", PaginatedUsage)
    app.add_directive("sdk-sphinx-copy-params", CopyParams)

    app.add_role("extdoclink", extdoclink_role)

    app.connect(
        "autodoc-process-signature", after_autodoc_signature_replace_MISSING_repr
    )

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
