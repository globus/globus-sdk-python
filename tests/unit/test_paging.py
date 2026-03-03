import json
from unittest import mock

import pytest
import requests

from globus_sdk.paging import HasNextPaginator, JSONAPIPaginator
from globus_sdk.response import GlobusHTTPResponse, IterableJSONAPIResponse
from globus_sdk.services.transfer.response import IterableTransferResponse

N = 25


class PagingSimulator:
    def __init__(self, n) -> None:
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


class JSONAPIPagingSimulator:

    def __init__(self, n) -> None:
        self.n = n  # the number of simulated items
        self.page_size = 10  # arbitrary page size

    def simulate_get(self, *args, **params):
        """
        Simulates a paginated response from a Globus API get supporting
        optional query_parameters and including a links object with a next
        link in the response using a simple id based page marker
        """
        query_params = params.get("query_params", {})
        marker = query_params.get("page[marker]")

        if not marker:
            marker = 0
        elif isinstance(marker, list):
            marker = int(marker[0])

        if marker > self.n:
            raise Exception("BadMarker")

        else:
            response_top_level = {
                "data": [],
            }
            for i in range(marker, min(self.n, marker + self.page_size)):
                response_top_level["data"].append(
                    {
                        "type": "foo",
                        "id": i,
                    }
                )

            # add links object with next link if there is remaining data
            if marker + self.page_size < self.n:
                next_marker = marker + self.page_size
                response_top_level["links"] = {
                    "next": f"https://foo.globus.org/foo?page[marker]={next_marker}"
                }

        # make the simulated response
        response = requests.Response()
        response._content = json.dumps(response_top_level).encode()
        response.headers["Content-Type"] = "application/json"
        return IterableJSONAPIResponse(GlobusHTTPResponse(response, mock.Mock()))


@pytest.fixture
def paging_simulator():
    return PagingSimulator(N)


@pytest.fixture
def jsonapi_paging_simulator():
    return JSONAPIPagingSimulator(N)


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
            yield from list(page)

    # confirm results
    for item, expected in zip(all_items(), range(N)):
        assert item["value"] == expected


def test_jsonapi_paginator(jsonapi_paging_simulator):
    """
    Walk the JSONAPIPagingSimulator with JSONAPIPaginator and confirm results are good
    """
    paginator = JSONAPIPaginator(
        jsonapi_paging_simulator.simulate_get,
        client_args=[],
        client_kwargs={},
    )

    def all_items():
        for page in paginator:
            yield from list(page)

    # confirm results
    for item, expected in zip(all_items(), range(N)):
        assert item["id"] == expected
