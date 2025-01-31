from xml.etree import ElementTree

import pytest


class DocutilsRunner:
    def __init__(self) -> None:
        from docutils.frontend import get_default_settings
        from docutils.parsers.rst import Parser

        self.parser = Parser()
        self.settings = get_default_settings(self.parser)

    def new_doc(self, doc_source="TEST"):
        from docutils.utils import new_document

        return new_document(doc_source, self.settings.copy())

    def parse_as_etree(self, source, doc):
        self.parser.parse(source, doc)
        # docutils produces 'xml.dom.minidom'
        # for a nicer API, convert to etree
        dom = doc.asdom()
        xml_string = dom.toxml()
        etree = ElementTree.fromstring(xml_string)
        # also, unlink the dom object to ensure we don't get cyclic references
        # which make GC fail to collect these (see xml.dom.minidom docs for detail)
        dom.unlink()
        return etree


@pytest.fixture
def sphinxext():
    """
    Provide the extension subpackage as a fixture so that we can properly capture
    skip requirements and avoid awkward import requirements.
    """
    pytest.importorskip("docutils", reason="testing sphinx extension needs docutils")

    import globus_sdk._sphinxext

    return globus_sdk._sphinxext


@pytest.fixture
def docutils_runner():
    pytest.importorskip("docutils", reason="testing sphinx extension needs docutils")
    return DocutilsRunner()


@pytest.fixture
def register_temporary_directive():
    pytest.importorskip("docutils", reason="testing sphinx extension needs docutils")
    from docutils.parsers.rst.directives import _directives, register_directive

    registered_names = []

    def func(name, directive):
        nonlocal registered_names
        registered_names.append(name)
        register_directive(name, directive)

    yield func

    for name in registered_names:
        del _directives[name]
