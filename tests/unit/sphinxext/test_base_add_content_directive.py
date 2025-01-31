import textwrap


def test_addcontent_generating_text(
    sphinxext, docutils_runner, register_temporary_directive
):

    class MyDirective(sphinxext.add_content_directive.AddContentDirective):
        def gen_rst(self):
            yield "a"
            yield "b"

    register_temporary_directive("mydirective", MyDirective)

    doc = docutils_runner.new_doc()
    etree = docutils_runner.parse_as_etree(".. mydirective::", doc)

    assert etree.tag == "document"
    assert etree.get("source") == "TEST"
    paragraph_element = etree.find("paragraph")
    assert paragraph_element is not None
    assert paragraph_element.text == textwrap.dedent(
        """\
        a
        b"""
    )


def test_addcontent_generating_warning(
    sphinxext, docutils_runner, register_temporary_directive
):

    class MyDirective(sphinxext.add_content_directive.AddContentDirective):
        def gen_rst(self):
            yield ".. note::"
            yield ""
            yield "     Some note content here."
            yield "     Multiline."

    register_temporary_directive("mydirective", MyDirective)

    doc = docutils_runner.new_doc()
    etree = docutils_runner.parse_as_etree(".. mydirective::", doc)

    assert etree.tag == "document"
    assert etree.get("source") == "TEST"
    note_element = etree.find("note")
    assert note_element is not None
    paragraph_element = note_element.find("paragraph")
    assert paragraph_element is not None
    assert paragraph_element.text == textwrap.dedent(
        """\
        Some note content here.
        Multiline."""
    )
