# type: ignore
"""
A Globus SDK Sphinx Extension for Autodoc of Class Methods
"""
from __future__ import annotations

import inspect
import json
from pydoc import locate

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles

from globus_sdk._testing import ResponseList


def _extract_known_scopes(scope_builder_name):
    sb = locate(scope_builder_name)
    return sb.scope_names


def _locate_class(classname):
    cls = locate(classname)
    if not inspect.isclass(cls):
        raise RuntimeError(
            f"uh-oh, {classname} is not a class name? type(classname)={type(cls)}"
        )
    return cls


def _classname2methods(classname, include_methods):
    """resolve a class name to a list of (public) method names
    takes a classname and a list of method names to avoid filtering out"""
    cls = _locate_class(classname)

    # get methods of the object as [(name, <unbound method>), ...]
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)

    def _methodname_is_good(m):
        if m in include_methods:
            return True
        # filter out dunder-methods and `_private` methods
        if m.startswith("_"):
            return False
        # filter out any inherited methods which are not overloaded
        if m not in cls.__dict__:
            return False
        return True

    return [(name, value) for name, value in methods if _methodname_is_good(name)]


def _is_paginated(func):
    return getattr(func, "_has_paginator", False)


class AddContentDirective(Directive):
    # Directive source:
    #   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/parsers/rst/__init__.py
    #
    # for information on how to write directives, see also:
    #   https://docutils.sourceforge.io/docs/howto/rst-directives.html#the-directive-class
    def gen_rst(self):
        return []

    def run(self):
        # implementation is based on the docs for parsing directive content as ReST doc:
        #   https://www.sphinx-doc.org/en/master/extdev/markupapi.html#parsing-directive-content-as-rest
        # which is how we will create rst here and have sphinx parse it

        # we need to add content lines into a ViewList which represents the content
        # of this directive, each one is appended with a "source" name
        # the best documentation for docutils is the source, so for ViewList, see...
        #   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/statemachine.py
        # writing the source name with angle-brackets seems to be the norm, but it's not
        # clear why -- perhaps docutils will care about the source in some way
        viewlist = ViewList()
        linemarker = "<" + self.__class__.__name__.lower() + ">"
        for line in self.gen_rst():
            viewlist.append(line, linemarker)

        # create a section node (it doesn't really matter what node type we use here)
        # and add the viewlist we just created as the children of the new node via the
        # nested_parse method
        # then return the children (i.e. discard the docutils node)
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, viewlist, node)
        return node.children


class AutoMethodList(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {"include_methods": directives.unchanged}

    def gen_rst(self):
        classname = self.arguments[0]

        include_methods = []
        if "include_methods" in self.options:
            include_methods = self.options["include_methods"].strip().split(",")

        yield ""
        yield "**Methods**"
        yield ""
        for methodname, method in _classname2methods(classname, include_methods):
            if not _is_paginated(method):
                yield f"* :py:meth:`~{classname}.{methodname}`"
            else:
                yield (
                    f"* :py:meth:`~{classname}.{methodname}`, "
                    f"``paginated.{methodname}()``"
                )

        yield ""


class ListKnownScopes(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "example_scope": directives.unchanged,
        # Allow overriding the base name to match how the ScopeBuilder will be accessed.
        "base_name": directives.unchanged,
    }

    def gen_rst(self):
        sb_name = self.arguments[0]
        sb_basename = sb_name.split(".")[-1]
        if "base_name" in self.options:
            sb_basename = self.options["base_name"]

        example_scope = None
        if "example_scope" in self.options:
            example_scope = self.options["example_scope"].strip()
        known_scopes = _extract_known_scopes(sb_name)
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


class EnumerateTestingFixtures(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "header_underline_char": directives.unchanged,
    }

    def gen_rst(self):
        from globus_sdk._testing import get_response_set

        underline_char = self.options.get("header_underline_char", "-")

        classname = self.arguments[0]
        cls = _locate_class(classname)
        service_name = cls.service_name

        yield classname
        yield underline_char * len(classname)
        yield ""
        yield (
            f":class:`{classname}` has registered responses "
            "for the following methods:"
        )
        yield ""
        for methodname, method in _classname2methods(classname, []):
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


def _derive_doc_url_base(service: str | None) -> str:
    if service is None:
        return "https://docs.globus.org/api"
    elif service == "groups":
        return "https://groups.api.globus.org/redoc#operation"
    elif service == "gcs":
        return "https://docs.globus.org/globus-connect-server/v5/api"
    elif service == "flows":
        return "https://globusonline.github.io/globus-flows#tag"
    elif service == "compute":
        return "https://compute.api.globus.org/redoc#tag"
    else:
        raise ValueError(f"Unsupported extdoclink service '{service}'")


def extdoclink_role(
    name,  # pylint: disable=unused-argument
    rawtext,
    text,
    lineno,  # pylint: disable=unused-argument
    inliner,  # pylint: disable=unused-argument
    options=None,  # pylint: disable=unused-argument
    content=None,  # pylint: disable=unused-argument
):
    if " " not in text:
        raise ValueError("extdoclink role must contain space-separated text")
    linktext, _, ref = text.rpartition(" ")
    if not ref.startswith("<") and ref.endswith(">"):
        raise ValueError("extdoclink role reference must be in angle brackets")
    ref = ref[1:-1]
    base_url = _derive_doc_url_base(None)
    node = nodes.reference(rawtext, linktext, refuri=f"{base_url}/{ref}")
    return [node], []


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

    def gen_rst(self):
        message = self.arguments[0].strip()

        service: str | None = self.options.get("service")
        default_base_url: str = _derive_doc_url_base(service)

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


class ExpandTestingFixture(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "case": directives.unchanged,
    }

    def gen_rst(self):
        from globus_sdk._testing import get_response_set

        response_set_name = self.arguments[0]
        casename = "default"
        if "case" in self.options:
            casename = self.options["case"].strip()
        response_set = get_response_set(response_set_name)
        response = response_set.lookup(casename)
        if isinstance(response, ResponseList):
            # If the default responses is a list of responses, use the first one
            response = response.responses[0]
        if response.json is not None:
            yield ".. code-block:: json"
            yield ""
            output_lines = json.dumps(
                response.json, indent=2, separators=(",", ": ")
            ).split("\n")
            for line in output_lines:
                yield f"    {line}"
        elif response.body is not None:
            yield ".. code-block:: text"
            yield ""
            output_lines = response.body.split("\n")
            for line in output_lines:
                yield f"    {line}"
        else:
            raise RuntimeError(
                "Error loading example content for response "
                f"{response_set_name}:{casename}. Neither JSON nor text body was found."
            )


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

    app.add_role("extdoclink", extdoclink_role)

    app.connect(
        "autodoc-process-signature", after_autodoc_signature_replace_MISSING_repr
    )

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
