from __future__ import annotations

import typing as t

from docutils.parsers.rst import directives

from ..utils import derive_doc_url_base
from .add_content_directive import AddContentDirective


class ExternalDocLink(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    # allow for spaces in the argument string
    final_argument_whitespace = True
    option_spec = {
        "base_url": directives.unchanged,
        "service": directives.unchanged,
        "ref": directives.unchanged_required,
    }

    def gen_rst(self) -> t.Iterator[str]:
        message = self.arguments[0].strip()

        service: str | None = self.options.get("service")
        default_base_url: str = derive_doc_url_base(service)

        base_url = self.options.get("base_url", default_base_url)
        relative_link = self.options["ref"]
        # use a trailing `__` to make the hyperlink an "anonymous hyperlink"
        #
        # the reason for this is that sphinx will warn (error with -W) if we generate
        # rst with duplicate target names, as when an autodoc method name matches the
        # (snake_cased) message for a hyperlink, a common scenario
        # the conflicts are stipulated by docutils to cause warnings, along with a
        # conflict resolution procedure specified under the implicit hyperlink section
        # of the spec:
        # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#implicit-hyperlink-targets
        #
        # for details on anonymous hyperlinks, see also:
        # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#anonymous-hyperlinks
        yield (
            f"See `{message} <{base_url}/{relative_link}>`__ in the "
            "API documentation for details."
        )
