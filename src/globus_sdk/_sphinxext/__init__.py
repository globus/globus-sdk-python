"""
A Globus SDK Sphinx Extension for Autodoc of Class Methods
"""

from __future__ import annotations

import typing as t

from sphinx.application import Sphinx

from .autodoc_hooks import after_autodoc_signature_replace_MISSING_repr
from .directives import (
    AutoMethodList,
    CopyParams,
    EnumerateTestingFixtures,
    ExpandTestingFixture,
    ExternalDocLink,
    ListKnownScopes,
    PaginatedUsage,
)
from .roles import extdoclink_role


def setup(app: Sphinx) -> dict[str, t.Any]:
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
