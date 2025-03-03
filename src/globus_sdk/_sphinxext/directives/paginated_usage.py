import typing as t

from .add_content_directive import AddContentDirective


class PaginatedUsage(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def gen_rst(self) -> t.Iterator[str]:
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
