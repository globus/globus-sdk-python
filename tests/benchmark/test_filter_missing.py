import copy

import pytest

from globus_sdk.testing import get_response_set
from globus_sdk.transport.representation_providers import RequestsRepresentationProvider


@pytest.mark.parametrize(
    ("width", "depth"),
    (
        # note that the expected number of objects is roughly "WIDTH raised to DEPTH"
        # so relatively modest numbers like 5x10 = 5 to the 10th = 9.7 million
        # be careful to build wide-but-shallow or deep-but-narrow trees
        pytest.param(1, 1, id="1w-1d"),
        pytest.param(5, 1, id="5w-1d"),
        pytest.param(1, 5, id="1w-5d"),
        pytest.param(1, 1000, id="1w-1000d"),
        pytest.param(5, 5, id="5w-5d"),
        pytest.param(10, 5, id="10w-5d"),
    ),
)
def test_deeply_nested_object_encoding(benchmark, depth, width):
    data = {}
    for _ in range(depth):
        data = {
            # significant optimization: if we're building something really deep with
            # width=1 we don't need to deepcopy
            f"nested{i}": data if width == 1 else copy.deepcopy(data)
            for i in range(width)
        }

    provider = RequestsRepresentationProvider()
    method = "POST"
    url = "https://example.api.globus.org/foo"
    params = {}
    headers = {}

    benchmark(provider.encode, method, url, params, data, headers)


# Use known response objects as "typical" JSON blobs.
# These aren't a perfect representative sample, but they're more realistically similar
# to request data than fully synthetic object graphs.
@pytest.mark.parametrize(
    "response_lookup_path",
    (
        "auth.get_consents",
        "transfer.create_tunnel",
        "flows.get_run_logs",
    ),
)
def test_typical_object_encoding(benchmark, response_lookup_path):
    response_set = get_response_set(response_lookup_path)
    data = response_set.lookup("default").json

    provider = RequestsRepresentationProvider()
    method = "POST"
    url = "https://example.api.globus.org/foo"
    params = {}
    headers = {}

    benchmark(provider.encode, method, url, params, data, headers)
