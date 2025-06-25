import re

import pytest


def test_listknownscopes_rejects_wrong_object_type(sphinx_runner, capsys):
    sphinx_runner.ensure_failure(
        ".. listknownscopes:: globus_sdk.BaseClient",
    )

    captured = capsys.readouterr()
    err_lines = captured.err.splitlines()

    test_line = None
    for line in err_lines:
        if "scope collection" in line:
            test_line = line
            break
    else:
        pytest.fail("Didn't find 'scope collection' in stderr")

    assert re.search(
        r"Expected <class '(\w+\.)+BaseClient'> to be a scope collection", test_line
    )


# choose an arbitrary scope collection from the SDK and confirm that listknownscopes
# will render its list of members
# for this case, we're using `TimersScopes`
def test_listknownscopes_of_timers(sphinx_runner):
    etree = sphinx_runner.to_etree(
        ".. listknownscopes:: globus_sdk.scopes.TimersScopes",
    )

    assert etree.tag == "document"

    paragraphs = etree.findall("paragraph")
    assert len(paragraphs) == 2
    paragraph0, paragraph1 = paragraphs

    assert paragraph0.text.startswith(
        "Various scopes are available as attributes of this object."
    )

    console_block = etree.find("doctest_block")
    assert console_block is not None
    assert console_block.text == ">>> TimersScopes.timer"

    emphasized_text = paragraph1.find("strong")
    assert emphasized_text is not None
    assert emphasized_text.text == "Supported Scopes"

    scope_list = etree.find("bullet_list")
    assert scope_list is not None
    scope_items = scope_list.findall("./list_item/paragraph/literal")
    assert len(scope_items) == 1
    assert scope_items[0].text == "timer"


def test_listknownscopes_of_timers_with_forced_example(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. listknownscopes:: globus_sdk.scopes.TimersScopes
            :example_scope: frobulate
        """,
    )

    assert etree.tag == "document"

    console_block = etree.find("doctest_block")
    assert console_block is not None
    assert console_block.text == ">>> TimersScopes.frobulate"


def test_listknownscopes_of_timers_with_altered_basename(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. listknownscopes:: globus_sdk.scopes.TimersScopes
            :base_name: ScopeMuddler
        """,
    )

    assert etree.tag == "document"

    console_block = etree.find("doctest_block")
    assert console_block is not None
    assert console_block.text == ">>> ScopeMuddler.timer"
