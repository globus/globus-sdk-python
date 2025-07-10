from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from globus_sdk import AuthLoginClient, IDTokenDecoder
    from globus_sdk._types import UUIDLike
    from globus_sdk.login_flows import LoginFlowManager
    from globus_sdk.token_storage import TokenStorage, TokenValidationError

    from .app import GlobusApp
    from .config import GlobusAppConfig


@t.runtime_checkable
class TokenStorageProvider(t.Protocol):
    r"""
    A protocol for a factory which can create ``TokenStorage``\s.

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


@t.runtime_checkable
class LoginFlowManagerProvider(t.Protocol):
    r"""
    A protocol for a factory which can create ``LoginFlowManager``\s.

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


@t.runtime_checkable
class IDTokenDecoderProvider(t.Protocol):
    r"""
    A protocol for a factory which can create ``IDTokenDecoder``\s.

    The SDK-provided ``IDTokenDecoder`` class supports this protocol.
    """

    @classmethod
    def for_globus_app(
        cls,
        *,
        app_name: str,
        config: GlobusAppConfig,
        login_client: AuthLoginClient,
    ) -> IDTokenDecoder:
        """
        Create an ``IDTokenDecoder`` for use in a GlobusApp.

        :param app_name: The name supplied to the GlobusApp.
        :param config: The configuration supplied to the GlobusApp.
        :param login_client: A login client to use for instantiating an
            ``IDTokenDecoder``.
        """


class TokenValidationErrorHandler(t.Protocol):
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
