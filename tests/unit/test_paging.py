import json
from unittest import mock

import pytest
import requests

from globus_sdk.paging import HasNextPaginator
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.services.transfer.response import IterableTransferResponse

N = 25


class PagingSimulator:
    def __init__(self, n):
        self.n = n  # the number of simulated items

    def simulate_get(self, *args, **params):
        """
        Simulates a paginated response from a Globus API get supporting limit,
        offset, and has next page
        """
        offset = params.get("offset", 0)
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
        response._content = json.dumps(data).encode()
        response.headers["Content-Type"] = "application/json"
        return IterableTransferResponse(GlobusHTTPResponse(response, mock.Mock()))


@pytest.fixture
def paging_simulator():
    return PagingSimulator(N)


def test_has_next_paginator(paging_simulator):
    """
    Walk the paging simulator with HasNextPaginator and confirm the results are good
    """
    paginator = HasNextPaginator(
        paging_simulator.simulate_get,
        get_page_size=lambda x: len(x["DATA"]),
        max_total_results=1000,
        page_size=10,
        client_args=[],
        client_kwargs={},
    )

    def all_items():
        for page in paginator:
            yield from page["DATA"]

    # confirm results
    for item, expected in zip(all_items(), range(N)):
        assert item["value"] == expected
