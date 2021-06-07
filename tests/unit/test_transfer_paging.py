import json
from unittest import mock

import pytest
import requests

from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.services.transfer.paging import PaginatedResource
from globus_sdk.services.transfer.response import IterableTransferResponse

N = 25


class PagingSimulator:
    def __init__(self, n):
        self.n = n  # the number of simulated items

    def simulate_get(self, path, params=None, headers=None, retry_401=True):
        """
        Simulates a paginated response from a Globus API get supporting limit,
        offset, and has next page
        """
        offset = params["offset"]
        limit = params["limit"]
        data = {}  # dict that will be treated as the json data of a response
        data["offset"] = offset
        data["limit"] = limit
        # fill data field
        data["DATA"] = []
        for i in range(offset, min(self.n, offset + limit)):
            data["DATA"].append({"value": i})
        # fill has_next_page field
        data["has_next_page"] = (offset + limit) < self.n

        # make the simulated response
        response = requests.Response()
        response._content = json.dumps(data).encode("utf-8")
        response.headers["Content-Type"] = "application/json"
        return IterableTransferResponse(
            GlobusHTTPResponse(response, client=mock.Mock())
        )


@pytest.fixture
def paging_simulator():
    return PagingSimulator(N)


def test_data(paging_simulator):
    """
    Gets data from PaginatedResource objects based on paging_simulator,
    confirms data is the expected range of numbers
    tests num_results < n, num_results > n, num_results = None,
    """
    # num_results < n
    less_results = N - 7
    pr_less = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=less_results,
    )
    # confirm results
    for item, expected in zip(pr_less.data, range(less_results)):
        assert item["value"] == expected

    assert pr_less.num_results_fetched == less_results

    # num_results > n
    more_results = N + 7
    pr_more = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=more_results,
    )
    # confirm results
    for item, expected in zip(pr_more.data, range(N)):
        assert item["value"] == expected
    assert pr_more.num_results_fetched == N

    # num_results = None (fetch all)
    pr_none = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=None,
    )
    # confirm results
    for item, expected in zip(pr_none.data, range(N)):
        assert item["value"] == expected
    assert pr_none.num_results_fetched == N

    # limit < N should show more results available
    pr_more_available = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=5,
    )

    # confirm results
    for item, expected in zip(pr_more_available.data, range(N)):
        assert item["value"] == expected
    assert pr_more_available.limit_less_than_available_results is True

    # limit > N should show no more results available
    pr_no_more_available = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=N,
    )

    # confirm results
    for item, expected in zip(pr_more_available.data, range(N)):
        assert item["value"] == expected
    assert pr_no_more_available.limit_less_than_available_results is False


def test_iterable_func(paging_simulator):
    """
    Gets the generator from a PaginatedResource's iterable_func,
    sanity checks usage
    """
    pr = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=None,
    )

    generator = pr.iterable_func()
    for i in range(N):
        assert next(generator)["value"] == i

    with pytest.raises(StopIteration):
        next(generator)
