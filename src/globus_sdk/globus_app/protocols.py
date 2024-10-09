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
    """
    A protocol for a factory which can create ``TokenStorages``.

    SDK-provided :ref:`token_storages` support this protocol.
    """

    @classmethod
    def for_globus_app(
        cls,
        *,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        namespace: str,
    ) -> TokenStorage:
        """
        Create a ``TokenStorage`` for use in a GlobusApp.

        :param app_name: The name supplied to the GlobusApp.
        :param config: The configuration supplied to the GlobusApp.
        :param client_id: The client_id of to the GlobusApp.
        :param namespace: A namespace to use for instantiating a TokenStorage.
        """


@runtime_checkable
class LoginFlowManagerProvider(Protocol):
    """
    A protocol for a factory which can create ``LoginFlowManagers``.

    SDK-provided :ref:`login_flow_managers` support this protocol.
    """

    @classmethod
    def for_globus_app(
        cls, *, app_name: str, config: GlobusAppConfig, login_client: AuthLoginClient
    ) -> LoginFlowManager:
        """
        Create a ``CommandLineLoginFlowManager`` for use in a GlobusApp.

        :param app_name: The name supplied to the GlobusApp.
        :param config: The configuration supplied to the GlobusApp.
        :param login_client: A login client to use for instantiating a LoginFlowManager.
        """


class TokenValidationErrorHandler(Protocol):
    """
    A handler invoked when a :class:`TokenValidationError` is raised during a
    service client call.

    If this call completes without raising an exception, the service client call
    will retry once more (subsequent errors will not call this handler).
    """

    def __call__(self, app: GlobusApp, error: TokenValidationError) -> None:
        """
        Resolve a token validation error.

        :param app: The GlobusApp instance which encountered an error.
        :param error: The error which was encountered.
        """
