"""
Unit tests for globus_sdk.SearchQuery
"""

import pytest

from globus_sdk import MISSING, RemovedInV4Warning, SearchQuery, SearchQueryV1
from globus_sdk._missing import filter_missing


def test_init_legacy():
    params = {"q": "foo", "limit": 10, "offset": 0, "advanced": False}
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        param_query = SearchQuery(**params)
    for par in params:
        assert param_query[par] == params[par]


def test_init_legacy_no_args():
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()

    assert len(filter_missing(query)) == 0


def test_init_legacy_additional_fields():
    add_params = {"param1": "value1", "param2": "value2"}
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        param_query = SearchQuery(additional_fields=add_params)
    for par in add_params:
        assert param_query[par] == add_params[par]


def test_init_legacy_deprecation_warning():
    with pytest.warns(
        RemovedInV4Warning,
        match="'SearchQuery' is deprecated. Use 'SearchQueryV1' instead.",
    ):
        SearchQuery()


def test_init_v1():
    query = SearchQueryV1()

    # ensure the version is set to query#1.0.0
    assert query["@version"] == "query#1.0.0"

    # ensure key attributes initialize to empty lists
    for attribute in ["facets", "filters", "post_facet_filters", "sort", "boosts"]:
        assert query[attribute] == MISSING

    # init with supported fields
    params = {"q": "foo", "limit": 10, "offset": 0, "advanced": False}
    param_query = SearchQueryV1(**params)
    for par in params:
        assert param_query[par] == params[par]

    # init with additional_fields
    add_params = {"param1": "value1", "param2": "value2"}
    param_query = SearchQueryV1(additional_fields=add_params)
    for par in add_params:
        assert param_query[par] == add_params[par]


@pytest.mark.parametrize("attrname", ["q", "limit", "offset", "advanced"])
def test_set_method(attrname):
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()
    method = getattr(query, "set_{}".format("query" if attrname == "q" else attrname))
    # start absent
    assert attrname not in filter_missing(query)
    # returns self
    assert method("foo") is query
    # sets value
    assert query[attrname] == "foo"


def test_add_facet():
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()
    assert "facets" not in query

    # simple terms facet
    # returns self
    assert query.add_facet("facetname", "fieldname") is query
    assert query["facets"]
    assert len(query["facets"]) == 1
    assert filter_missing(query["facets"][0]) == {
        "type": "terms",
        "name": "facetname",
        "field_name": "fieldname",
    }

    # terms with size
    query.add_facet("n", "f", size=5)
    assert len(query["facets"]) == 2
    assert filter_missing(query["facets"][1]) == {
        "type": "terms",
        "name": "n",
        "field_name": "f",
        "size": 5,
    }

    # date histogram
    query.add_facet(
        "n",
        "f",
        type="date_histogram",
        date_interval="year",
        histogram_range=(1870, 1880),
    )
    assert len(query["facets"]) == 3
    assert filter_missing(query["facets"][2]) == {
        "type": "date_histogram",
        "name": "n",
        "field_name": "f",
        "date_interval": "year",
        "histogram_range": {"low": 1870, "high": 1880},
    }

    # unknown param
    query.add_facet(
        "facetname", "fieldname", additional_fields={"nonexistentparam": "value1"}
    )
    assert len(query["facets"]) == 4
    assert filter_missing(query["facets"][3]) == {
        "type": "terms",
        "name": "facetname",
        "field_name": "fieldname",
        "nonexistentparam": "value1",
    }


def test_add_filter():
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()
    assert "filters" not in query

    # returns self
    assert query.add_filter("f", [1, 2, 3]) is query

    assert query["filters"]
    assert len(query["filters"]) == 1
    assert query["filters"][0] == {
        "field_name": "f",
        "type": "match_all",
        "values": [1, 2, 3],
    }

    # match_any + custom param
    query.add_filter(
        "f",
        [1, 2, 3],
        type="match_any",
        additional_fields={"nonexistentparam": "val1"},
    )
    assert len(query["filters"]) == 2
    assert query["filters"][1] == {
        "field_name": "f",
        "type": "match_any",
        "values": [1, 2, 3],
        "nonexistentparam": "val1",
    }

    # range
    query.add_filter("f", [{"from": 1, "to": 100}], type="range")
    assert len(query["filters"]) == 3
    assert query["filters"][2] == {
        "field_name": "f",
        "type": "range",
        "values": [{"from": 1, "to": 100}],
    }


def test_add_boost():
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()
    assert "boosts" not in query

    # returns self
    assert query.add_boost("f", 2) == query

    assert query["boosts"]
    assert len(query["boosts"]) == 1
    assert query["boosts"][0] == {"field_name": "f", "factor": 2}

    # custom param
    query.add_boost("f", 1.1, additional_fields={"nonexistentparam": "value1"})
    assert len(query["boosts"]) == 2
    assert query["boosts"][1] == {
        "field_name": "f",
        "factor": 1.1,
        "nonexistentparam": "value1",
    }


def test_add_sort():
    with pytest.warns(RemovedInV4Warning, match="'SearchQuery' is deprecated"):
        query = SearchQuery()
    assert "sort" not in query

    # returns self
    assert query.add_sort("f") is query

    assert query["sort"]
    assert len(query["sort"]) == 1
    assert filter_missing(query["sort"][0]) == {"field_name": "f"}

    # with order
    query.add_sort("f", order="asc")
    assert len(query["sort"]) == 2
    assert query["sort"][1] == {"field_name": "f", "order": "asc"}

    # custom param
    query.add_sort("f", order="asc", additional_fields={"nonexistentparam": "value1"})
    assert len(query["sort"]) == 3
    assert query["sort"][2] == {
        "field_name": "f",
        "order": "asc",
        "nonexistentparam": "value1",
    }
