from __future__ import annotations

from datetime import datetime

from globus_sdk import Scope
from globus_sdk._types import UUIDLike


class MissingIdentityError(ValueError):
    pass


class TokenValidationError(Exception):
    pass


class MissingTokensError(Exception):
    pass


class IdentityMismatchError(TokenValidationError):
    def __init__(self, message: str, stored_id: UUIDLike, new_id: UUIDLike):
        super().__init__(message)
        self.stored_id = stored_id
        self.new_id = new_id


class ExpiredTokenError(TokenValidationError):
    def __init__(self, expires_at_seconds: int):
        expiration = datetime.utcfromtimestamp(expires_at_seconds)
        super().__init__(f"Token expired at {expiration.isoformat()}")
        self.expiration = expiration


class UnmetScopeRequirementsError(TokenValidationError):
    def __init__(self, message: str, scope_requirements: dict[str, list[Scope]]):
        super().__init__(message)
        self.scope_requirements = scope_requirements
