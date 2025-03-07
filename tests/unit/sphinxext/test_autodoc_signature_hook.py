import pytest


@pytest.fixture
def process_signature(sphinxext):
    def func(signature, return_annotation):
        return sphinxext.after_autodoc_signature_replace_MISSING_repr(
            object(), "", "", object(), None, signature, return_annotation
        )

    return func


def test_autodoc_signature_MISSING_hook_skips_nulls(process_signature):
    assert process_signature(None, None) == (None, None)


def test_autodoc_signature_MISSING_hook_can_update_signature(process_signature):
    input_sig = "(x: str | <globus_sdk.MISSING> = <globus_sdk.MISSING>, y: int)"
    output_sig, output_annotation = process_signature(input_sig, "str")
    assert output_annotation == "str"
    assert output_sig == "(x: str | MISSING = MISSING, y: int)"


def test_autodoc_signature_MISSING_hook_can_update_return_type(process_signature):
    input_sig = "(x: str | int = 0, y: int = 0)"
    output_sig, output_annotation = process_signature(
        input_sig, "int | <globus_sdk.MISSING>"
    )
    assert input_sig == output_sig
    assert output_annotation == "int | MISSING"
