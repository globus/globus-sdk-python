import textwrap

import pytest

import globus_sdk


def test_locate_class_finds_transfer_client(sphinxext):
    assert (
        sphinxext.utils.locate_class("globus_sdk.TransferClient")
        is globus_sdk.TransferClient
    )


def test_locate_class_rejects_missing(sphinxext):
    with pytest.raises(RuntimeError, match="MISSING is not a class name"):
        sphinxext.utils.locate_class("globus_sdk.MISSING")


def test_read_sphinx_params(sphinxext):
    docstring = """
    preamble

    :param param1: some doc on one line
    :param param2: other doc
        spanning multiple lines
    :param param3: a doc
        spanning
        many
        lines
    :param param4: a doc
        spanning lines

        with a break in the middle ^
    :param param5: another


    :param param6: and a final one after some whitespace

    epilogue
    """
    params = sphinxext.utils.read_sphinx_params(docstring)
    assert len(params) == 6
    assert params[0] == ":param param1: some doc on one line"
    assert params[1] == ":param param2: other doc\n    spanning multiple lines"
    assert params[2] == textwrap.dedent(
        """\
        :param param3: a doc
            spanning
            many
            lines"""
    )
    assert params[3] == textwrap.dedent(
        """\
        :param param4: a doc
            spanning lines

            with a break in the middle ^"""
    )
    assert params[4] == ":param param5: another"
    assert params[5] == ":param param6: and a final one after some whitespace"

    # clear the cache after the test
    # not essential, but reduces the risk that this impacts some future test
    sphinxext.utils.read_sphinx_params.cache_clear()
