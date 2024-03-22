"""
Constructs which are added to `experimental` ultimately (hopefully) get ported over to
  the main `globus_sdk` namespace.

The tests in this module verify that those constructs are still available from the
  `globus_sdk.experimental` namespace (for backwards compatibility).

Eventually these constructs do get deprecated at which point the tests in this module
  can be deleted.
"""


def test_scope_importable_from_experimental():
    from globus_sdk.experimental.scope_parser import (  # noqa: F401
        Scope,
        ScopeCycleError,
        ScopeParseError,
    )
