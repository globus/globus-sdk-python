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


def test_login_flow_manager_importable_from_experimental():
    with pytest.warns(RemovedInV4Warning):
        from globus_sdk.experimental.login_flow_manager import (  # noqa: F401
            CommandLineLoginFlowManager,
            LocalServerLoginFlowManager,
            LoginFlowManager,
        )
