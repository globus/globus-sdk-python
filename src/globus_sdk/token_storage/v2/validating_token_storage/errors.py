from __future__ import annotations

from datetime import datetime

from globus_sdk import GlobusError, Scope
from globus_sdk._types import UUIDLike


class TokenValidationError(GlobusError):
    """The class of errors raised when a token fails validation."""


class IdentityValidationError(TokenValidationError):
    """
    The class of errors raised when a token response's identity is indeterminate or
    incorrect.
    """


class MissingIdentityError(IdentityValidationError, LookupError):
    """No identity info contained in a token response."""


class IdentityMismatchError(IdentityValidationError, ValueError):
    """The identity in a token response did not match the expected identity."""

    def __init__(self, message: str, stored_id: UUIDLike, new_id: UUIDLike) -> None:
        super().__init__(message)
        self.stored_id = stored_id
        self.new_id = new_id


class MissingTokenError(TokenValidationError, LookupError):
    """No token stored for a given resource server."""

    def __init__(self, message: str, resource_server: str) -> None:
        super().__init__(message)
        self.resource_server = resource_server


class ExpiredTokenError(TokenValidationError, ValueError):
    """The token stored for a given resource server has expired."""

    def __init__(self, expires_at_seconds: int) -> None:
        expiration = datetime.fromtimestamp(expires_at_seconds)
        super().__init__(f"Token expired at {expiration.isoformat()}")
        self.expiration = expiration


class UnmetScopeRequirementsError(TokenValidationError, ValueError):
    """The token stored for a given resource server is missing required scopes."""

    def __init__(
        self, message: str, scope_requirements: dict[str, list[Scope]]
    ) -> None:
        super().__init__(message)
        # The full set of scope requirements which were evaluated.
        #   Notably this is not exclusively the unmet scope requirements.
        self.scope_requirements = scope_requirements
