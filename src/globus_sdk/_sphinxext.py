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
    option_spec = {"example_scope": directives.unchanged}

    def gen_rst(self):
        sb_name = self.arguments[0]
        sb_basename = sb_name.split(".")[-1]

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

    def gen_rst(self):
        from globus_sdk._testing import get_response_set

        classname = self.arguments[0]
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
                yield f'* :py:attr:`~{classname}.{methodname}` (``case="{casename}"``)'
        yield ""


class ExternalDocLink(AddContentDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    # allow for spaces in the argument string
    final_argument_whitespace = True
    option_spec = {"mode": directives.unchanged, "ref": directives.unchanged_required}

    def gen_rst(self):
        message = self.arguments[0].strip()

        mode = "default"
        if "mode" in self.options:
            mode = self.options["mode"]

        if mode == "default":
            base_url = "https://docs.globus.org/api"
            relative_link = self.options["ref"]

            yield (
                f"See `{message} <{base_url}/{relative_link}>`_ in the "
                "API documentation for details."
            )
        elif mode in (
            "groups",
            "gcs",
        ):
            raise ValueError(f"Unsupported extdoclink mode {mode}. TODO: add support")
        else:
            raise ValueError(f"Unsupported extdoclink mode {mode}")


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


def setup(app):
    app.add_directive("automethodlist", AutoMethodList)
    app.add_directive("listknownscopes", ListKnownScopes)
    app.add_directive("enumeratetestingfixtures", EnumerateTestingFixtures)
    app.add_directive("expandtestfixture", ExpandTestingFixture)
    app.add_directive("extdoclink", ExternalDocLink)
    app.add_directive("paginatedusage", PaginatedUsage)
