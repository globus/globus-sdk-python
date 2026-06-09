from __future__ import annotations

import sys
import typing as t

__all__ = (
    "ORJSON_AVAILABLE",
    "loads",
    "dumps",
)


try:
    import orjson

    ORJSON_AVAILABLE: bool = True
except ImportError:
    ORJSON_AVAILABLE = False


def require() -> None:
    """Raise an error if orjson is not available."""
    if not ORJSON_AVAILABLE:
        raise RuntimeError(
            "'orjson' is not available but globus-sdk was configured to use it. "
            "This is not valid. Please ensure that 'orjson' is installed."
        )


if t.TYPE_CHECKING:
    from orjson import dumps, loads
else:

    def __dir__() -> list[str]:
        return ["__all__", "__file__", "__path__"] + list(__all__)

    def __getattr__(name: str) -> t.Any:
        require()

        mod = sys.modules[__name__]
        if name in ("loads", "dumps"):
            value = getattr(orjson, name)
            setattr(mod, name, value)
            return value

        raise AttributeError(f"module {__name__} has no attribute {name}")
