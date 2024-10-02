"""
Constructs which are added to `experimental` ultimately (hopefully) get ported over to
  the main `globus_sdk` namespace.

The tests in this module verify that those constructs are still available from the
  `globus_sdk.experimental` namespace (for backwards compatibility).

Eventually these constructs do get deprecated at which point the tests in this module
  can be deleted.
"""

import pytest

from globus_sdk import RemovedInV4Warning
from globus_sdk.gare import (
    GARE,
    GlobusAuthorizationParameters,
    has_gares,
    is_gare,
    to_gare,
    to_gares,
)


def test_scope_importable_from_experimental():
    from globus_sdk.experimental.scope_parser import (  # noqa: F401
        Scope,
        ScopeCycleError,
        ScopeParseError,
    )


@pytest.mark.parametrize(
    "alias, value",
    (
        ("GlobusAuthorizationParameters", GlobusAuthorizationParameters),
        ("GlobusAuthRequirementsError", GARE),
        ("to_auth_requirements_error", to_gare),
        ("to_auth_requirements_errors", to_gares),
        ("has_auth_requirements_errors", has_gares),
        ("is_auth_requirements_error", is_gare),
    ),
)
def test_deprecated_experimental_alias(alias, value):
    with pytest.warns(RemovedInV4Warning):
        from globus_sdk.experimental import (
            auth_requirements_error as experimental_module,
        )

        aliased_value = getattr(experimental_module, alias)
    assert aliased_value is value


def test_login_flow_manager_importable_from_experimental():
    with pytest.warns(RemovedInV4Warning):
        from globus_sdk.experimental.login_flow_manager import (  # noqa: F401
            CommandLineLoginFlowManager,
            LocalServerLoginFlowManager,
            LoginFlowManager,
        )


def test_tokenstorage_importable_from_experimental():
    with pytest.warns(RemovedInV4Warning):
        from globus_sdk.experimental.tokenstorage import (  # noqa: F401
            JSONTokenStorage,
            MemoryTokenStorage,
            SQLiteTokenStorage,
        )


def test_globus_app_importable_from_experimental():
    # This construct should be imported from `globus_sdk.globus_app`.
    with pytest.warns(RemovedInV4Warning, match=r"globus_sdk\.globus_app\."):
        from globus_sdk.experimental.globus_app import (  # noqa: F401
            TokenValidationErrorHandler,
        )

    # Each of these constructs should be imported from `globus_sdk`.
    # This regex ensures we didn't include `globus_sdk.globus_app.` in any warning
    with pytest.warns(RemovedInV4Warning, match=r"^(?!globus_sdk\.globus_app\.).*$"):
        from globus_sdk.experimental.globus_app import (  # noqa: F401
            ClientApp,
            GlobusApp,
            GlobusAppConfig,
            UserApp,
        )
