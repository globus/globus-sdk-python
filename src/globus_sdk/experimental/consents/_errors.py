from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from ._model import Consent


class ConsentParseError(Exception):
    """An error raised if consent parsing/loading fails."""

    def __init__(self, message: str, raw_consent: dict[str, t.Any]):
        super().__init__(message)
        self.raw_consent = raw_consent


class ConsentTreeConstructionError(Exception):
    """An error raised if consent tree construction fails."""

    def __init__(self, message: str, consents: list[Consent]):
        super().__init__(message)
        self.consents = consents
