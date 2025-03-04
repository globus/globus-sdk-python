import typing as t

from docutils.parsers.rst import directives

import globus_sdk

from ..utils import classname2methods, locate_class
from .add_content_directive import AddContentDirective


class EnumerateTestingFixtures(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "header_underline_char": directives.unchanged,
    }

    def gen_rst(self) -> t.Iterator[str]:
        from globus_sdk._testing import get_response_set

        underline_char = self.options.get("header_underline_char", "-")

        classname = self.arguments[0]
        cls = locate_class(classname)
        if not issubclass(cls, globus_sdk.BaseClient):
            msg = f"Expected {cls} to be a subclass of BaseClient"
            raise RuntimeError(msg)
        service_name = cls.service_name

        yield classname
        yield underline_char * len(classname)
        yield ""
        yield (
            f":class:`{classname}` has registered responses "
            "for the following methods:"
        )
        yield ""
        for methodname, method in classname2methods(classname, []):
            try:
                rset = get_response_set(method)
                # success -> has a response
            except ValueError:
                continue
                # error -> has no response, continue
            for casename in rset.cases():
                # use "attr" rather than "meth" so that sphinx does not add parens
                # the use of the method as an attribute of the class or instance better
                # matches how `_testing` handles things
                yield (
                    ".. dropdown:: "
                    f':py:attr:`~{classname}.{methodname}` (``case="{casename}"``)'
                )
                yield ""
                yield f"    .. expandtestfixture:: {service_name}.{methodname}"
                yield f"       :case: {casename}"
                yield ""
        yield ""
