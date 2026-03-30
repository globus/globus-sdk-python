import importlib
import sys
import typing as t

__all__ = (
    "TransferClientV2",
    "TunnelCreateDocument",
    "TunnelUpdateDocument",
)


# imports from `globus_sdk.experimental.transfer_v2` are done lazily to ensure
# that we do not eagerly import `requests` when attempting to use SDK
# components which do not need it
if t.TYPE_CHECKING:
    from .transfer_v2 import (
        TransferClientV2,
        TunnelCreateDocument,
        TunnelUpdateDocument,
    )
else:
    _LAZY_IMPORT_TABLE = {
        "transfer_v2": {
            "TransferClientV2",
            "TunnelCreateDocument",
            "TunnelUpdateDocument",
        }
    }

    def __getattr__(name: str) -> t.Any:
        for modname, items in _LAZY_IMPORT_TABLE.items():
            if name in items:
                mod = importlib.import_module("." + modname, __name__)
                value = getattr(mod, name)
                setattr(sys.modules[__name__], name, value)
                return value

        raise AttributeError(f"module {__name__} has no attribute {name}")
