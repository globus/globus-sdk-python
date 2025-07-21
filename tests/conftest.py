from unittest import mock

import pytest
import responses

import globus_sdk
from globus_sdk.transport import RequestsTransport


@pytest.fixture(autouse=True)
def mocksleep():
    with mock.patch("time.sleep") as m:
        yield m


@pytest.fixture
def no_retry_transport():
    return RequestsTransport(max_retries=0)


@pytest.fixture(autouse=True)
def mocked_responses():
    """
    All tests enable `responses` patching of the `requests` package, replacing
    all HTTP calls.
    """
    responses.start()

    yield

    responses.stop()
    responses.reset()


@pytest.fixture
def make_response():
    def _make_response(
        response_class=None,
        status=200,
        headers=None,
        json_body=None,
        text=None,
        client=None,
    ):
        """
        Construct and return an SDK response object with a mocked requests.Response

        Unlike mocking of an API route, this is meant for unit testing in which we
        want to directly create the response.
        """
        from tests.common import PickleableMockResponse

        r = PickleableMockResponse(
            status, headers=headers, json_body=json_body, text=text
        )
        http_res = globus_sdk.GlobusHTTPResponse(
            r, client=client if client is not None else mock.Mock()
        )
        if response_class is not None:
            return response_class(http_res)
        return http_res

    return _make_response
