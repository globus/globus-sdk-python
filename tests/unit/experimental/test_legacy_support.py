"""
Constructs which are added to `experimental` ultimately (hopefully) get ported over to
  the main `globus_sdk` namespace.

The tests in this module verify that those constructs are still available from the
  `globus_sdk.experimental` namespace (for backwards compatibility).

Eventually these constructs do get deprecated at which point the tests in this module
  can be deleted.
"""

import pytest


def test_scope_importable_from_experimental():
    from globus_sdk.experimental.scope_parser import (  # noqa: F401
        Scope,
        ScopeCycleError,
        ScopeParseError,
    )


def test_login_flow_manager_importable_from_experimental():
    with pytest.warns(DeprecationWarning):
        from globus_sdk.experimental.login_flow_manager import (  # noqa: F401
            CommandLineLoginFlowManager,
            LocalServerLoginFlowManager,
            LoginFlowManager,
        )


def test_tokenstorage_importable_from_experimental():
    with pytest.warns(DeprecationWarning):
        from globus_sdk.experimental.tokenstorage import (  # noqa: F401
            JSONTokenStorage,
            MemoryTokenStorage,
            SQLiteTokenStorage,
        )
