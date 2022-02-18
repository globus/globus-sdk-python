import random
import uuid

import pytest
import responses

from globus_sdk.paging import Paginator
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


# multiple pages of results, very stubby
SHARED_ENDPOINT_RESULTS = [
    {
        "next_token": "token1",
        "shared_endpoints": [{"id": "abcd"} for x in range(1000)],
    },
    {
        "next_token": "token2",
        "shared_endpoints": [{"id": "abcd"} for x in range(1000)],
    },
    {
        "next_token": None,
        "shared_endpoints": [{"id": "abcd"} for x in range(100)],
    },
]


def test_shared_endpoint_list_non_paginated(client):
    # add each page
    for page in SHARED_ENDPOINT_RESULTS:
        register_api_route(
            "transfer", "/endpoint/endpoint_id/shared_endpoint_list", json=page
        )

    # without calling the paginated version, we only get one page
    res = client.get_shared_endpoint_list("endpoint_id")
    assert len(list(res)) == 1000
    for item in res:
        assert "id" in item


@pytest.mark.parametrize("paging_variant", ["attr", "wrap"])
def test_shared_endpoint_list_iter_pages(client, paging_variant):
    # add each page
    for page in SHARED_ENDPOINT_RESULTS:
        register_api_route(
            "transfer", "/endpoint/endpoint_id/shared_endpoint_list", json=page
        )

    # paginator pages() call gets an iterator of pages
    if paging_variant == "attr":
        paginator = client.paginated.get_shared_endpoint_list("endpoint_id")
    elif paging_variant == "wrap":
        paginator = Paginator.wrap(client.get_shared_endpoint_list)("endpoint_id")
    else:
        raise NotImplementedError
    count = 0
    for item in paginator.pages():
        count += 1
        assert "shared_endpoints" in item

    assert count == 3


@pytest.mark.parametrize("paging_variant", ["attr", "wrap"])
def test_shared_endpoint_list_iter_items(client, paging_variant):
    # add each page
    for page in SHARED_ENDPOINT_RESULTS:
        register_api_route(
            "transfer", "/endpoint/endpoint_id/shared_endpoint_list", json=page
        )

    # paginator items() call gets an iterator of individual page items
    if paging_variant == "attr":
        paginator = client.paginated.get_shared_endpoint_list("endpoint_id")
    elif paging_variant == "wrap":
        paginator = Paginator.wrap(client.get_shared_endpoint_list)("endpoint_id")
    else:
        raise NotImplementedError
    count = 0
    for item in paginator.items():
        count += 1
        assert "id" in item

    assert count == 2100


@pytest.mark.parametrize("paging_variant", ["attr", "wrap"])
def test_task_skipped_errors_pagination(client, paging_variant):
    task_id = str(uuid.uuid1())
    # add each page (10 pages)
    for page_number in range(10):
        page_data = []
        for item_number in range(100):
            page_data.append(
                {
                    "DATA_TYPE": "skipped_error",
                    "checksum_algorithm": None,
                    "destination_path": f"/~/{page_number}-{item_number}.txt",
                    "error_code": "PERMISSION_DENIED",
                    "error_details": "Error bad stuff happened",
                    "error_time": "2022-02-18T19:06:05+00:00",
                    "external_checksum": None,
                    "is_delete_destination_extra": False,
                    "is_directory": False,
                    "is_symlink": False,
                    "source_path": f"/~/{page_number}-{item_number}.txt",
                }
            )
        register_api_route(
            "transfer",
            f"/task/{task_id}/skipped_errors",
            json={
                "DATA_TYPE": "skipped_errors",
                "next_marker": f"mark{page_number}" if page_number < 9 else None,
                "DATA": page_data,
            },
        )

    # paginator items() call gets an iterator of individual page items
    if paging_variant == "attr":
        paginator = client.paginated.task_skipped_errors(task_id)
    elif paging_variant == "wrap":
        paginator = Paginator.wrap(client.task_skipped_errors)(task_id)
    else:
        raise NotImplementedError
    count = 0
    for item in paginator.items():
        count += 1
        assert item["DATA_TYPE"] == "skipped_error"

    assert count == 1000
