import pathlib
import shutil
import tempfile
import textwrap
from xml.etree import ElementTree

import pytest
import responses

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent.parent


#
# sphinx's intersphinx plugin loads an inventory from the docs.python.org docs for
# linkage each time it runs
# we use a cached copy so that:
# - tests don't require the network
# - we don't put unnecessary load on the python docs site
# - tests will be faster
#
@pytest.fixture(autouse=True)
def _mock_intersphinx_object_inventory_response(mocked_responses):
    objects_inv = HERE / "objects.inv"
    responses.get(
        url="https://docs.python.org/3/objects.inv", body=objects_inv.read_bytes()
    )


class SingleFileSphinxRunner:
    """
    A SingleFileSphinxRunner runs sphinx with the full globus-sdk config loaded, against
    some target RST source, and returns the parsed XML it produces.

    For content with sphinx-specific features like `py:meth` and other sphinx domain
    features, this is the best way of ensuring we get a realistic build with good
    outputs.

    Primarily, usage should use ``to_etree`` like so:

    >>> def test_my_thing(sphinx_runner):
    >>>     etree_element = sphinx_runner.to_etree(
    >>>         ":py:class:`globus_sdk.TimersClient`"
    >>>     )

    Because it's often difficult to know the structure of the produced XML, if
    `debug=True` is passed, this will print the full XML to stdout, for you to
    see in your test outputs.
    """

    def to_etree(self, content, dedent=True, debug=False):
        from sphinx.cmd.build import build_main as sphinx_main

        if dedent:
            content = textwrap.dedent(content)

        source_dir = tempfile.TemporaryDirectory()
        out_dir = tempfile.TemporaryDirectory()
        with source_dir, out_dir:
            self._prepare_file(source_dir.name, content, "index.rst")
            self._prepare_sphinx_config(source_dir.name)

            sphinx_rc = sphinx_main([source_dir.name, out_dir.name, "-b", "xml"])

            assert sphinx_rc == 0

            output_xml = pathlib.Path(out_dir.name) / "index.xml"
            xml_text = output_xml.read_text()
            if debug:
                print("--- debug from sphinx runner ---")
                print()
                print(xml_text)
                print()
                print("--- end debug from sphinx runner ---")
            return ElementTree.fromstring(xml_text)

    def ensure_failure(self, content, dedent=True, debug=False):
        from sphinx.cmd.build import build_main as sphinx_main

        if dedent:
            content = textwrap.dedent(content)

        source_dir = tempfile.TemporaryDirectory()
        out_dir = tempfile.TemporaryDirectory()
        with source_dir, out_dir:
            self._prepare_file(source_dir.name, content, "index.rst")
            self._prepare_sphinx_config(source_dir.name)

            sphinx_rc = sphinx_main([source_dir.name, out_dir.name, "-b", "xml"])
            assert sphinx_rc != 0

    def _prepare_file(self, source_dir, content, filename):
        source_path = pathlib.Path(source_dir) / filename
        source_path.write_text(content)

    def _prepare_sphinx_config(self, source_dir):
        shutil.copy(
            REPO_ROOT / "docs" / "conf.py", pathlib.Path(source_dir) / "conf.py"
        )


class DocutilsRunner:
    """
    A DocutilsRunner is a direct user of docutils, with no special sphinx customizations
    applied.

    It can fail on sphinx-specific content, but it lets us directly test underlying
    docutils behaviors.

    Primarily, usage should use ``to_etree`` like so:

    >>> def test_my_thing(docutils_runner):
    >>>     etree_element = docutils_runner.to_etree(
    >>>         ".. note:: a note directive"
    >>>     )

    Because it's often difficult to know the structure of the produced XML, if
    `debug=True` is passed, this will print the full XML to stdout, for you to
    see in your test outputs.
    """

    def __init__(self) -> None:
        from docutils.frontend import get_default_settings
        from docutils.parsers.rst import Parser

        self.parser = Parser()
        self.settings = get_default_settings(self.parser)
        # set the halt_level so that docutils won't "power through" noncritical errors
        #   https://docutils.sourceforge.io/docs/user/config.html#halt-level
        self.settings.halt_level = 2

    def to_etree(self, content, dedent=True, debug=False):

        if dedent:
            content = textwrap.dedent(content)

        doc = self.new_doc()
        xml_string = self.make_xml(content, doc)
        if debug:
            print("--- debug from docutils runner ---")
            print()
            print(xml_string)
            print()
            print("--- end debug from docutils runner ---")
        etree = ElementTree.fromstring(xml_string)
        return etree

    def new_doc(self, doc_source="TEST"):
        from docutils.utils import new_document

        return new_document(doc_source, self.settings.copy())

    def make_xml(self, source, doc):
        # docutils produces 'xml.dom.minidom'
        # for a nicer API, convert to XML so we can reparse as etree
        self.parser.parse(source, doc)
        dom = doc.asdom()
        xml_string = dom.toxml()
        # also, unlink the dom object to ensure we don't get cyclic references
        # which make GC fail to collect these (see xml.dom.minidom docs for detail)
        dom.unlink()
        return xml_string


@pytest.fixture
def sphinx_runner():
    pytest.importorskip("sphinx", reason="testing sphinx extension needs sphinx")

    return SingleFileSphinxRunner()


@pytest.fixture
def docutils_runner():
    pytest.importorskip("docutils", reason="testing sphinx extension needs docutils")
    return DocutilsRunner()


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
