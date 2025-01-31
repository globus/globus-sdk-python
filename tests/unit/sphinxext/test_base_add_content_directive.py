import textwrap


def test_addcontent_generating_text(
    sphinxext, docutils_runner, register_temporary_directive
):

    class MyDirective(sphinxext.custom_directives.AddContentDirective):
        def gen_rst(self):
            yield "a"
            yield "b"

    register_temporary_directive("mydirective", MyDirective)

    etree = docutils_runner.to_etree(".. mydirective::")

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

    class MyDirective(sphinxext.custom_directives.AddContentDirective):
        def gen_rst(self):
            yield ".. note::"
            yield ""
            yield "     Some note content here."
            yield "     Multiline."

    register_temporary_directive("mydirective", MyDirective)

    etree = docutils_runner.to_etree(".. mydirective::")

    assert etree.tag == "document"
    assert etree.get("source") == "TEST"
    note_element = etree.find("note")
    assert note_element is not None
    paragraph_element = note_element.find("paragraph")
    assert paragraph_element is not None
    assert paragraph_element.text == "Some note content here.\nMultiline."
