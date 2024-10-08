from __future__ import annotations

import dataclasses
import typing as t

from globus_sdk.config import get_environment_name
from globus_sdk.login_flows import (
    CommandLineLoginFlowManager,
    LocalServerLoginFlowManager,
    LoginFlowManager,
)
from globus_sdk.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    SQLiteTokenStorage,
    TokenStorage,
    TokenValidationError,
)
from globus_sdk.tokenstorage.v2.validating_token_storage import IdentityMismatchError

from .protocols import (
    LoginFlowManagerProvider,
    TokenStorageProvider,
    TokenValidationErrorHandler,
)

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
    An immutable dataclass used to control the behavior of a :class:`GlobusApp`.

    :ivar bool request_refresh_tokens: Whether to request ``refresh tokens`` (expire
        after 6 months of no use) or use exclusively ``access tokens`` (expire 2 hours
        after issuance). Default: ``False``.

    :ivar str | ``TokenStorage`` | ``TokenStorageProvider`` token_storage:
        A class responsible for storing and retrieving tokens.
        This may be either a well-known provider (one of
        :class:`"json" <globus_sdk.tokenstorage.JSONTokenStorage>`,
        :class:`"sqlite" <globus_sdk.tokenstorage.SQLiteTokenStorage>`, or
        :class:`"memory" <globus_sdk.tokenstorage.MemoryTokenStorage>`) or a custom
        storage/provider. Default: ``"json"``.

    :ivar str | ``LoginFlowManager`` | ``LoginFlowManagerProvider`` login_flow_manager:
        A class responsible for overseeing Globus Auth login flows.
        This may be either be a well-known provider (one of
        :class:`"command-line" <globus_sdk.login_flows.CommandLineLoginFlowManager>` or
        :class:`"local-server" <globus_sdk.login_flows.LocalServerLoginFlowManager>`)
        or a custom manager/provider. Default: ``"command-line"``.

        .. note::

            **login_flow_manager** may be ignored when using a :class:`ClientApp`.

    :ivar str | None login_redirect_uri: The destination for Globus Auth to send
        a user after once completed a login flow. Default: ``None``.

        .. note::

            **login_redirect_url** may be ignored when using a
            :class:`NativeAppAuthClient`.
            Explicit values must be pre-registered on your client
            `here <https://app.globus.org/settings/developers>`_.

    :ivar ``TokenValidationErrorHandler`` token_validation_error_handler: A handler
        invoked to resolve errors raised during token validation.
        Default: ``resolve_by_login_flow`` (runs a login flow, storing the resulting
        tokens).

    :ivar str environment: The Globus environment of services to interact with. This is
        mostly used for testing purposes. This may additionally be set with the
        environment variable `GLOBUS_SDK_ENVIRONMENT`. Default: ``"production"``.
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
