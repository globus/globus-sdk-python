from __future__ import annotations

import dataclasses
import typing as t

from globus_sdk.config import get_environment_name
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LocalServerLoginFlowManager,
    LoginFlowManager,
)
from globus_sdk.experimental.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    SQLiteTokenStorage,
    TokenStorage,
)

from ._types import (
    LoginFlowManagerProvider,
    TokenStorageProvider,
    TokenValidationErrorHandler,
)
from .errors import IdentityMismatchError, TokenValidationError

if t.TYPE_CHECKING:
    from .app import GlobusApp


KnownLoginFlowManager = t.Literal["command-line", "local-server"]
KNOWN_LOGIN_FLOW_MANAGERS: dict[KnownLoginFlowManager, LoginFlowManagerProvider] = {
    "command-line": CommandLineLoginFlowManager,
    "local-server": LocalServerLoginFlowManager,
}
KnownTokenStorage = t.Literal["json", "sqlite", "memory"]
KNOWN_TOKEN_STORAGES: dict[KnownTokenStorage, t.Type[TokenStorageProvider]] = {
    "json": JSONTokenStorage,
    "sqlite": SQLiteTokenStorage,
    "memory": MemoryTokenStorage,
}


def resolve_by_login_flow(app: GlobusApp, error: TokenValidationError) -> None:
    """
    An error handler for GlobusApp token access errors that will retry the
    login flow if the error is a TokenValidationError.

    :param app: The GlobusApp instance which encountered an error.
    :param error: The encountered token validation error.
    """
    if isinstance(error, IdentityMismatchError):
        # An identity mismatch error indicates incorrect use of the app. Not something
        #   that can be resolved by running a login flow.
        raise error

    app.login(force=True)


@dataclasses.dataclass(frozen=True)
class GlobusAppConfig:
    """
    Various configuration options for controlling the behavior of a ``GlobusApp``.

    :param login_flow_manager: An optional ``LoginFlowManager`` instance, provider,
        or identifier ("command-line" or "local-server").
        For a ``UserApp``, defaults to "command-line".
        For a ``ClientApp``, this value is not supported.
    :param login_redirect_uri: The redirect URI to use for login flows.
        For a "local-server" login flow manager, this value is not supported.
        For a native client, this value defaults to a globus-hosted helper page.
        For a confidential client, this value is required.
    :param request_refresh_tokens: If True, the ``GlobusApp`` will request refresh
        tokens for long-lived access.
    :param token_storage: A ``TokenStorage`` instance, provider, or identifier
        ("json", "sqlite", or "memory").
        Default: "json"
    :param token_validation_error_handler: A callable that will be called when a
        token validation error is encountered. The default behavior is to retry the
        login flow automatically.
    :param environment: The Globus environment being targeted by this app. This is
        predominately for internal use and can be ignored in most cases.
    """

    login_flow_manager: (
        KnownLoginFlowManager | LoginFlowManagerProvider | LoginFlowManager | None
    ) = None
    login_redirect_uri: str | None = None
    token_storage: KnownTokenStorage | TokenStorageProvider | TokenStorage = "json"
    request_refresh_tokens: bool = False
    token_validation_error_handler: TokenValidationErrorHandler | None = (
        resolve_by_login_flow
    )
    environment: str = dataclasses.field(default_factory=get_environment_name)


DEFAULT_CONFIG: GlobusAppConfig = GlobusAppConfig()
