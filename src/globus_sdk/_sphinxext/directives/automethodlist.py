import types
import typing as t

from docutils.parsers.rst import directives

from ..utils import classname2methods
from .add_content_directive import AddContentDirective


class AutoMethodList(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {"include_methods": directives.unchanged}

    def gen_rst(self) -> t.Iterator[str]:
        classname = self.arguments[0]

        include_methods = []
        if "include_methods" in self.options:
            include_methods = self.options["include_methods"].strip().split(",")

        yield ""
        yield "**Methods**"
        yield ""
        for methodname, method in classname2methods(classname, include_methods):
            if not is_paginated_method(method):
                yield f"* :py:meth:`~{classname}.{methodname}`"
            else:
                yield (
                    f"* :py:meth:`~{classname}.{methodname}`, "
                    f"``paginated.{methodname}()``"
                )

        yield ""


def is_paginated_method(func: types.FunctionType) -> bool:
    return getattr(func, "_has_paginator", False)
