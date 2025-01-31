import typing as t

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles


class AddContentDirective(Directive):
    # Directive source:
    #   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/parsers/rst/__init__.py
    #
    # for information on how to write directives, see also:
    #   https://docutils.sourceforge.io/docs/howto/rst-directives.html#the-directive-class
    def gen_rst(self) -> t.Iterator[str]:
        yield from []

    def run(self) -> t.Sequence[Node]:
        # implementation is based on the docs for parsing directive content as ReST doc:
        #   https://www.sphinx-doc.org/en/master/extdev/markupapi.html#parsing-directive-content-as-rest
        # which is how we will create rst here and have sphinx parse it

        # we need to add content lines into a ViewList which represents the content
        # of this directive, each one is appended with a "source" name
        # the best documentation for docutils is the source, so for ViewList, see...
        #   https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/statemachine.py
        # writing the source name with angle-brackets seems to be the norm, but it's not
        # clear why -- perhaps docutils will care about the source in some way
        viewlist = StringList()
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
