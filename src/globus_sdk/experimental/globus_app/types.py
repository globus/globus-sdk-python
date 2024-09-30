from __future__ import annotations

import sys
import typing as t

from globus_sdk import AuthLoginClient
from globus_sdk._types import UUIDLike
from globus_sdk.login_flows import LoginFlowManager
from globus_sdk.tokenstorage import TokenStorage

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable

if t.TYPE_CHECKING:
    from globus_sdk.tokenstorage import TokenValidationError

    from .app import GlobusApp
    from .config import GlobusAppConfig


@runtime_checkable
class TokenStorageProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls,
        *,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        namespace: str,
    ) -> TokenStorage: ...


@runtime_checkable
class LoginFlowManagerProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls, *, app_name: str, config: GlobusAppConfig, login_client: AuthLoginClient
    ) -> LoginFlowManager: ...


class TokenValidationErrorHandler(Protocol):
    def __call__(self, app: GlobusApp, error: TokenValidationError) -> None: ...
