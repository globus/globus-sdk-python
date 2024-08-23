"""
Test that Timers objects are available under their legacy names
(via supported paths only) and that they emit deprecation warnings
as appropriate.
"""

import pytest

import globus_sdk
import globus_sdk.scopes


def test_importing_legacy_scope_name_works_but_warns():
    # first, remove the object from the module's `__dict__` if it was there
    # ensures that access will run `__getattr__`
    if "TimerScopes" in globus_sdk.scopes.__dict__:
        del globus_sdk.scopes.__dict__["TimerScopes"]

    with pytest.warns(
        globus_sdk.exc.RemovedInV4Warning, match="'TimerScopes' is a deprecated name"
    ):
        from globus_sdk.scopes import TimerScopes
    assert TimerScopes is globus_sdk.scopes.TimersScopes
    assert hasattr(globus_sdk.scopes, "TimerScopes")


def test_bad_access_to_legacy_name_errors():
    # sanity check that by adding module-level 'getattr' we haven't broken the
    # AttributeError behaviors of the module
    with pytest.raises(
        ImportError, match="cannot import name 'FOO' from 'globus_sdk.scopes'"
    ):
        from globus_sdk.scopes import FOO  # noqa: F401

    with pytest.raises(AttributeError, match="globus_sdk.scopes has no attribute BAR"):
        globus_sdk.scopes.BAR


def test_importing_legacy_error_name_works():
    # first, remove the object from the module's `__dict__` if it was there
    # ensures that access will run `__getattr__`
    if "TimerAPIError" in globus_sdk.__dict__:
        del globus_sdk.__dict__["TimerAPIError"]

    from globus_sdk import TimerAPIError, TimersAPIError

    assert TimerAPIError is TimersAPIError
    assert hasattr(globus_sdk, "TimerAPIError")


def test_importing_legacy_client_name_works():
    # first, remove the object from the module's `__dict__` if it was there
    # ensures that access will run `__getattr__`
    if "TimerClient" in globus_sdk.__dict__:
        del globus_sdk.__dict__["TimerClient"]

    from globus_sdk import TimerClient, TimersClient

    assert TimerClient is TimersClient
    assert hasattr(globus_sdk, "TimerClient")
