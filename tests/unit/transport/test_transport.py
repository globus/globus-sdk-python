import pathlib

import pytest

from globus_sdk.transport import RequestsTransport, RetryContext
from globus_sdk.transport.requests import _exponential_backoff


def _linear_backoff(ctx: RetryContext) -> float:
    if ctx.backoff is not None:
        return ctx.backoff
    return 0.5 * (2**ctx.attempt)


ca_bundle_file = pathlib.Path(__file__).parent.parent.absolute() / "CA-Bundle.cert"
ca_bundle_directory = ca_bundle_file.parent
ca_bundle_non_existent = ca_bundle_directory / "bogus.bogus"


@pytest.mark.parametrize(
    "param_name, init_value, tune_value",
    [
        ("verify_ssl", True, True),
        ("verify_ssl", True, False),
        ("verify_ssl", True, ca_bundle_file),
        ("verify_ssl", True, str(ca_bundle_file)),
        ("verify_ssl", True, ca_bundle_directory),
        ("verify_ssl", True, str(ca_bundle_directory)),
        ("verify_ssl", True, ca_bundle_non_existent),
        ("verify_ssl", True, str(ca_bundle_non_existent)),
        ("http_timeout", 60, 120),
        ("retry_backoff", _exponential_backoff, _linear_backoff),
        ("max_sleep", 10, 10),
        ("max_sleep", 10, 1),
        ("max_retries", 0, 5),
        ("max_retries", 10, 0),
    ],
)
def test_transport_tuning(param_name, init_value, tune_value):
    expected_value = (
        str(tune_value) if isinstance(tune_value, pathlib.Path) else tune_value
    )
    init_kwargs = {param_name: init_value}
    transport = RequestsTransport(**init_kwargs)

    assert getattr(transport, param_name) == init_value

    tune_kwargs = {param_name: tune_value}
    with transport.tune(**tune_kwargs):
        assert getattr(transport, param_name) == expected_value

    assert getattr(transport, param_name) == init_value


def test_transport_can_manipulate_user_agent():
    transport = RequestsTransport()

    # starting state -- the user agent is visible and equivalent in two places
    assert "User-Agent" in transport.headers
    assert transport.headers["User-Agent"] == transport.user_agent

    # setting it slash-appends it to the base agent (in both places)
    transport.user_agent = "frobulator-1.0"
    assert (
        transport.headers["User-Agent"] == f"{transport.BASE_USER_AGENT}/frobulator-1.0"
    )
    assert transport.user_agent == f"{transport.BASE_USER_AGENT}/frobulator-1.0"

    # deleting it doesn't clear the property
    # but accessing the property doesn't add it back into the dict
    del transport.headers["User-Agent"]
    assert transport.user_agent == f"{transport.BASE_USER_AGENT}/frobulator-1.0"
    assert "User-Agent" not in transport.headers

    # but updating it will add it back
    transport.user_agent = "demuddler-2.2"
    assert (
        transport.headers["User-Agent"] == f"{transport.BASE_USER_AGENT}/demuddler-2.2"
    )
    assert transport.user_agent == f"{transport.BASE_USER_AGENT}/demuddler-2.2"


def test_transport_can_manipulate_client_info():
    transport = RequestsTransport()

    # starting state -- the clientinfo is visible in headers
    # and a fake product is not
    assert "X-Globus-Client-Info" in transport.headers
    assert "frobulator" not in transport.headers["X-Globus-Client-Info"]

    # we can add said product to the header
    transport.globus_client_info.add({"product": "frobulator", "version": "1.0"})
    assert "product=frobulator,version=1.0" in transport.headers["X-Globus-Client-Info"]

    # clearing the client info removes the header
    transport.globus_client_info.clear()
    assert "X-Globus-Client-Info" not in transport.headers

    # adding a product re-adds the header
    transport.globus_client_info.add({"product": "demuddler", "version": "8.8"})
    assert "product=demuddler,version=8.8" in transport.headers["X-Globus-Client-Info"]


def test_double_clear_of_client_info_is_allowed():
    # clear the client info twice -- catching any potential bugs with `del ...` or
    # similar assumptions that the value is present
    transport = RequestsTransport()
    transport.globus_client_info.clear()
    transport.globus_client_info.clear()
    assert "X-Globus-Client-Info" not in transport.headers
