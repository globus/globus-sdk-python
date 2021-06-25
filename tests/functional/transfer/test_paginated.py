import random

import pytest
import responses

from tests.common import register_api_route

# empty search
EMPTY_SEARCH_RESULT = {
    "DATA_TYPE": "endpoint_list",
    "offset": 0,
    "limit": 100,
    "has_next_page": False,
    "DATA": [],
}

# single page of data
SINGLE_PAGE_SEARCH_RESULT = {
    "DATA_TYPE": "endpoint_list",
    "offset": 0,
    "limit": 100,
    "has_next_page": False,
    "DATA": [
        {"DATA_TYPE": "endpoint", "display_name": f"SDK Test Stub {x}"}
        for x in range(100)
    ],
}

# multiple pages of results, very stubby
MULTIPAGE_SEARCH_RESULTS = [
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 0,
        "limit": 100,
        "has_next_page": True,
        "DATA": [
            {"DATA_TYPE": "endpoint", "display_name": f"SDK Test Stub {x}"}
            for x in range(100)
        ],
    },
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 100,
        "limit": 100,
        "has_next_page": True,
        "DATA": [
            {
                "DATA_TYPE": "endpoint",
                "display_name": f"SDK Test Stub {x + 100}",
            }
            for x in range(100, 200)
        ],
    },
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 200,
        "limit": 100,
        "has_next_page": False,
        "DATA": [
            {
                "DATA_TYPE": "endpoint",
                "display_name": f"SDK Test Stub {x + 200}",
            }
            for x in range(100)
        ],
    },
]


def _mk_task_doc(idx):
    return {
        "DATA_TYPE": "task",
        "source_endpoint_id": "dc8e1110-b698-11eb-afd7-e1e7a67e00c1",
        "source_endpoint_display_name": "foreign place",
        "destination_endpoint_id": "83567b16-478d-4ead-a486-645bab0b07dc",
        "destination_endpoint_display_name": "my home",
        "directories": 0,
        "effective_bytes_per_second": random.randint(0, 10000),
        "files": 1,
        "encrypt_data": False,
        "label": f"autogen transfer {idx}",
    }


MULTIPAGE_TASK_LIST_RESULTS = [
    {
        "DATA_TYPE": "task_list",
        "offset": 0,
        "limit": 100,
        "total": 200,
        "DATA": [_mk_task_doc(x) for x in range(100)],
    },
    {
        "DATA_TYPE": "task_list",
        "offset": 100,
        "limit": 200,
        "total": 200,
        "DATA": [_mk_task_doc(x) for x in range(100, 200)],
    },
]


def test_endpoint_search_noresults(client):
    register_api_route("transfer", "/endpoint_search", json=EMPTY_SEARCH_RESULT)

    res = client.endpoint_search("search query!")
    assert res["DATA"] == []


def test_endpoint_search_one_page(client):
    register_api_route("transfer", "/endpoint_search", json=SINGLE_PAGE_SEARCH_RESULT)

    # without calling the paginated version, we only get one page
    res = client.endpoint_search("search query!")
    assert len(list(res)) == 100
    assert res["DATA_TYPE"] == "endpoint_list"
    for res_obj in res:
        assert res_obj["DATA_TYPE"] == "endpoint"


@pytest.mark.parametrize("method", ("__iter__", "pages"))
@pytest.mark.parametrize(
    "api_methodname,paged_data",
    [
        ("endpoint_search", MULTIPAGE_SEARCH_RESULTS),
        ("task_list", MULTIPAGE_TASK_LIST_RESULTS),
    ],
)
def test_paginated_method_multipage(client, method, api_methodname, paged_data):
    if api_methodname == "endpoint_search":
        route = "/endpoint_search"
        client_method = client.endpoint_search
        paginated_method = client.paginated.endpoint_search
        call_args = ("search_query",)
        wrapper_type = "endpoint_list"
        data_type = "endpoint"
    elif api_methodname == "task_list":
        route = "/task_list"
        client_method = client.task_list
        paginated_method = client.paginated.task_list
        call_args = ()
        wrapper_type = "task_list"
        data_type = "task"
    else:
        raise NotImplementedError

    # add each page
    for page in paged_data:
        register_api_route("transfer", route, json=page)

    # unpaginated, we'll only get one page
    res = list(client_method(*call_args))
    assert len(res) == 100

    # reset and reapply responses
    responses.reset()
    for page in paged_data:
        register_api_route("transfer", route, json=page)

    # setup the paginator and either point at `pages()` or directly at the paginator's
    # `__iter__`
    paginator = paginated_method(*call_args)
    if method == "pages":
        iterator = paginator.pages()
    elif method == "__iter__":
        iterator = paginator
    else:
        raise NotImplementedError

    # paginated calls gets all pages
    count_pages = 0
    count_objects = 0
    for page in iterator:
        count_pages += 1
        assert page["DATA_TYPE"] == wrapper_type
        for res_obj in page:
            count_objects += 1
            assert res_obj["DATA_TYPE"] == data_type

    assert count_pages == len(paged_data)
    assert count_objects == sum(len(x["DATA"]) for x in paged_data)


def test_endpoint_search_multipage_iter_items(client):
    # add each page
    for page in MULTIPAGE_SEARCH_RESULTS:
        register_api_route("transfer", "/endpoint_search", json=page)

    # paginator items() call gets an iterator of individual page items
    paginator = client.paginated.endpoint_search("search_query")
    count_objects = 0
    for item in paginator.items():
        count_objects += 1
        assert item["DATA_TYPE"] == "endpoint"

    assert count_objects == sum(len(x["DATA"]) for x in MULTIPAGE_SEARCH_RESULTS)
