import typing as t
from pydoc import locate

from ..utils import read_sphinx_params
from .add_content_directive import AddContentDirective


class CopyParams(AddContentDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 0

    def gen_rst(self) -> t.Iterator[str]:
        source_object_name: str = self.arguments[0]
        if not source_object_name.startswith("globus_sdk"):
            source_object_name = f"globus_sdk.{source_object_name}"

        source_object = locate(source_object_name)

        content: t.Iterable[str]
        if self.content:
            content = iter(self.content)
        else:
            content = ()

        for line in content:
            if line.strip() == "<YIELD>":
                break
            yield line

        yield from read_sphinx_params(source_object.__doc__)

        for line in content:
            yield line
