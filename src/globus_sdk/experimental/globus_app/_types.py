from __future__ import annotations

import sys
import typing as t

from globus_sdk import AuthLoginClient
from globus_sdk._types import UUIDLike
from globus_sdk.experimental.login_flow_manager import LoginFlowManager
from globus_sdk.experimental.tokenstorage import TokenStorage

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable

if t.TYPE_CHECKING:
    from .app import GlobusApp
    from .config import GlobusAppConfig
    from .errors import TokenValidationError


@runtime_checkable
class TokenStorageProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls, client_id: UUIDLike, app_name: str, config: GlobusAppConfig, namespace: str
    ) -> TokenStorage: ...


@runtime_checkable
class LoginFlowManagerProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> LoginFlowManager: ...


class TokenValidationErrorHandler(Protocol):
    def __call__(self, app: GlobusApp, error: TokenValidationError) -> None: ...
