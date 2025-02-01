import pytest


def test_paginated_usage_requires_an_argument(
    sphinxext, docutils_runner, register_temporary_directive
):
    register_temporary_directive(
        "paginatedusage", sphinxext.custom_directives.PaginatedUsage
    )

    with pytest.raises(Exception, match=r"1 argument\(s\) required, 0 supplied\."):
        docutils_runner.to_etree(".. paginatedusage::")


def test_paginated_usage_simple(sphinx_runner):
    etree = sphinx_runner.to_etree(".. paginatedusage:: foo")
    assert etree.tag == "document"
    paragraph = etree.find("paragraph")
    assert paragraph is not None
    text_parts = list(paragraph.itertext())
    assert text_parts[0].startswith("This method supports paginated access.")

    code_block = etree.find("literal_block")
    assert code_block is not None
    assert code_block.get("language") == "default"
    assert code_block.text == "client.paginated.foo(...)"
