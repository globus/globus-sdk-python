"""
A Globus SDK Sphinx Extension for Autodoc of Class Methods

NOTE: this only works correctly under python3, where unbound methods are functions
"""
import inspect
from pydoc import locate

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles


def _classname2methods(classname, include_methods):
    """resolve a class name to a list of (public) method names
    takes a classname and a list of method names to avoid filtering out"""
    klass = locate(classname)
    if not inspect.isclass(klass):
        raise RuntimeError(
            "uh-oh, {} is not a class name? type(classname)={}".format(
                classname, type(klass)
            )
        )

    # get methods of the object as [(name, <unbound method>), ...]
    methods = inspect.getmembers(klass, predicate=inspect.isfunction)

    def _methodname_is_good(m):
        if m in include_methods:
            return True
        # filter out dunder-methods and `_private` methods
        if m.startswith("_"):
            return False
        # filter out any inherited methods which are not overloaded
        if m not in klass.__dict__:
            return False
        return True

    return [(name, value) for name, value in methods if _methodname_is_good(name)]


def _is_paginated(func):
    return getattr(func, "_has_paginator", False)


class AutoMethodList(Directive):
    # Directive source:
    #   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/parsers/rst/__init__.py
    has_content = False
    required_arguments = 1
    optional_arguments = 1

    def gen_rst(self):
        classname = self.arguments[0]

        include_methods = []
        for arg in self.arguments[1:]:
            if arg.startswith("include_methods="):
                include_methods = [x for x in arg.split("=")[1].split(",")]

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
        for line in self.gen_rst():
            viewlist.append(line, "<automethodlist>")

        # create a section node (it doesn't really matter what node type we use here)
        # and add the viewlist we just created as the children of the new node via the
        # nested_parse method
        # then return the children (i.e. discard the docutils node)
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, viewlist, node)
        return node.children


def setup(app):
    app.add_directive("automethodlist", AutoMethodList)
