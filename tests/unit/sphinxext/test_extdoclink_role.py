import pytest


def test_extdoclink_role_rejects_no_spaces(sphinxext):
    with pytest.raises(
        ValueError, match="extdoclink role must contain space-separated text"
    ):
        sphinxext.extdoclink_role("ref", "foobar", "foobar", 0, object())


def test_extdoclink_role_requires_angle_brackets(sphinxext):
    with pytest.raises(
        ValueError, match="extdoclink role reference must be in angle brackets"
    ):
        sphinxext.extdoclink_role("ref", "foo bar", "foo bar", 0, object())


def test_extdoclink_role_simple(sphinxext):
    nodes, _ = sphinxext.extdoclink_role(
        "ref", "foo bar &lt;baz/quxx&gt;", "foo bar <baz/quxx>", 0, object()
    )
    assert len(nodes) == 1
    node = nodes[0]
    assert node["refuri"] == "https://docs.globus.org/api/baz/quxx"
