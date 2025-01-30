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
