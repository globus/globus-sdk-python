import pytest

from globus_sdk.transport import RequestsTransport, RetryContext
from globus_sdk.transport.requests import _exponential_backoff


def _linear_backoff(ctx: RetryContext) -> float:
    if ctx.backoff is not None:
        return ctx.backoff
    return 0.5 * (2**ctx.attempt)


@pytest.mark.parametrize(
    "param_name, init_value, tune_value",
    [
        ("verify_ssl", True, True),
        ("verify_ssl", True, False),
        ("http_timeout", 60, 120),
        ("retry_backoff", _exponential_backoff, _linear_backoff),
        ("max_sleep", 10, 10),
        ("max_sleep", 10, 1),
        ("max_retries", 0, 5),
        ("max_retries", 10, 0),
    ],
)
def test_transport_tuning(param_name, init_value, tune_value):
    init_kwargs = {param_name: init_value}
    transport = RequestsTransport(**init_kwargs)

    assert getattr(transport, param_name) == init_value

    tune_kwargs = {param_name: tune_value}
    with transport.tune(**tune_kwargs):
        assert getattr(transport, param_name) == tune_value

    assert getattr(transport, param_name) == init_value
