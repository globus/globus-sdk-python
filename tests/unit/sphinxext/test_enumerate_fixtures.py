import json
import re
import types

import pytest

import globus_sdk


def test_enumerate_fixtures_rejects_wrong_object_type(sphinx_runner, capsys):
    sphinx_runner.ensure_failure(
        ".. enumeratetestingfixtures:: globus_sdk.NullAuthorizer",
    )

    captured = capsys.readouterr()
    err_lines = captured.err.splitlines()

    test_line = None
    for line in err_lines:
        if "BaseClient" in line:
            test_line = line
            break
    else:
        pytest.fail("Didn't find 'BaseClient' in stderr")

    assert re.search(
        r"Expected <class '(\w+\.)+NullAuthorizer'> to be a subclass of BaseClient",
        test_line,
    )


# choose an arbitrary client to test against
def test_enumerate_fixtures_of_search_client(sphinx_runner):
    etree = sphinx_runner.to_etree(
        ".. enumeratetestingfixtures:: globus_sdk.SearchClient",
    )
    assert etree.tag == "document"

    title = etree.find("./section/title")
    assert title.text == "globus_sdk.SearchClient"

    dropdowns = etree.findall("./section/container[@design_component='dropdown']")
    # we don't care about exactly what methods are found and produced as dropdowns
    # we just want to make sure there are "some"
    assert len(dropdowns) > 1

    # grab the first dropdown and inspect it
    first_dropdown = dropdowns[0]
    # find the title, make sure it matches a real method
    fixture_title = first_dropdown.find("./rubric/literal")
    assert fixture_title is not None
    first_method_name = fixture_title.text
    assert hasattr(globus_sdk.SearchClient, first_method_name)
    first_method = getattr(globus_sdk.SearchClient, first_method_name)
    assert isinstance(first_method, types.FunctionType)

    # for each dropdown, there should be a content area and it should contain valid JSON
    for dropdown in dropdowns:
        fixture_title = dropdown.find("./rubric/literal").text
        example_block = dropdown.find("./literal_block")
        assert example_block is not None
        assert example_block.get("language") == "json"
        content = example_block.text
        try:
            json.loads(content)
        except json.JSONDecodeError:
            pytest.fail(
                f"{fixture_title} in SearchClient fixture docs didn't have JSON content"
            )
