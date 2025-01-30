import pytest


@pytest.fixture
def sphinxext():
    """
    Provide the extension subpackage as a fixture so that we can properly capture
    skip requirements and avoid awkward import requirements.
    """
    pytest.importorskip("docutils", reason="testing sphinx extension needs docutils")

    import globus_sdk._sphinxext

    return globus_sdk._sphinxext
