import json

import pytest


def test_expand_testing_fixture_fails_on_bad_reference(sphinx_runner, capsys):
    sphinx_runner.ensure_failure(
        ".. expandtestfixture:: NO_SUCH_FIXTURE",
    )

    captured = capsys.readouterr()
    err_lines = captured.err.splitlines()

    test_line = None
    for line in err_lines:
        if "ValueError: no fixtures defined" in line:
            test_line = line
            break
    else:
        pytest.fail("Didn't find 'ValueError: no fixtures defined' in stderr")

    assert (
        "no fixtures defined for globus_sdk.testing.data.NO_SUCH_FIXTURE" in test_line
    )


# choose an arbitrary example fixture to test
def test_expand_testing_fixture_on_valid_fixture(sphinx_runner):
    etree = sphinx_runner.to_etree(
        ".. expandtestfixture:: groups.set_group_policies",
    )

    code_block = etree.find("./literal_block")
    assert code_block is not None
    assert code_block.get("language") == "json"

    # check against the known values for this fixture
    data = json.loads(code_block.text)
    assert data["is_high_assurance"] is False
    assert data["group_visibility"] == "private"


# choose an arbitrary example fixture to test with multiple cases
def test_expand_testing_fixture_on_non_default_case(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. expandtestfixture:: auth.userinfo
            :case: unauthorized
        """,
    )

    code_block = etree.find("./literal_block")
    assert code_block is not None
    assert code_block.get("language") == "json"

    # check against the known values for this fixture
    data = json.loads(code_block.text)
    assert data["error_description"] == "Unauthorized"
    assert data["errors"][0]["status"] == "401"
