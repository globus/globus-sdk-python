"""
A Globus SDK Sphinx Extension for Autodoc of Class Methods
"""

from __future__ import annotations

from .custom_directives import (
    AddContentDirective,
    AutoMethodList,
    EnumerateTestingFixtures,
    ExpandTestingFixture,
    ExternalDocLink,
    ListKnownScopes,
)
from .roles import extdoclink_role


class PaginatedUsage(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def gen_rst(self):
        yield "This method supports paginated access. "
        yield "To use the paginated variant, give the same arguments as normal, "
        yield "but prefix the method name with ``paginated``, as in"
        yield ""
        yield ".. code-block::"
        yield ""
        yield f"    client.paginated.{self.arguments[0]}(...)"
        yield ""
        yield "For more information, see"
        yield ":ref:`how to make paginated calls <making_paginated_calls>`."


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


def after_autodoc_signature_replace_MISSING_repr(  # pylint: disable=missing-param-doc,missing-type-doc  # noqa: E501
    app,  # pylint: disable=unused-argument
    what,  # pylint: disable=unused-argument
    name,  # pylint: disable=unused-argument
    obj,  # pylint: disable=unused-argument
    options,  # pylint: disable=unused-argument
    signature: str,
    return_annotation: str,
):
    """
    convert <globus_sdk.MISSING> to MISSING in autodoc signatures

    :param signature: the signature after autodoc parsing/rendering
    :param return_annotation: the return type annotation, including the leading `->`,
        after autodoc parsing/rendering
    """
    if signature is not None:
        signature = signature.replace("<globus_sdk.MISSING>", "MISSING")
    if return_annotation is not None:
        return_annotation = return_annotation.replace("<globus_sdk.MISSING>", "MISSING")
    return signature, return_annotation


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
