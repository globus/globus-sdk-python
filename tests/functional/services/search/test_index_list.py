from globus_sdk._testing import load_response


def test_search_index_list(client):
    meta = load_response(client.index_list).metadata
    index_ids = meta["index_ids"]

    res = client.index_list()
    assert res.http_status == 200

    index_list = res["index_list"]
    assert isinstance(index_list, list)
    assert len(index_list) == len(index_ids)
    assert [i["id"] for i in index_list] == index_ids


def test_search_index_list_is_iterable(client):
    meta = load_response(client.index_list).metadata
    index_ids = meta["index_ids"]

    res = client.index_list()
    assert res.http_status == 200

    index_list = list(res)
    assert len(index_list) == len(index_ids)
    assert [i["id"] for i in index_list] == index_ids
