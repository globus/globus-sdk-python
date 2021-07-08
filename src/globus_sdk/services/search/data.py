from typing import Any, Dict, Optional

from globus_sdk import utils


class SearchQuery(utils.PayloadWrapper):
    """
    A specialized dict which has helpers for creating and modifying a Search
    Query document.

    Example usage:

    >>> from globus_sdk import SearchClient, SearchQuery
    >>> sc = SearchClient(...)
    >>> index_id = ...
    >>> query = (SearchQuery(q='example query')
    >>>          .set_limit(100).set_offset(10)
    >>>          .add_filter('path.to.field1', ['foo', 'bar']))
    >>> result = sc.post_search(index_id, query)
    """

    def __init__(
        self,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        advanced: Optional[bool] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        if q is not None:
            self["q"] = q
        if limit is not None:
            self["limit"] = limit
        if offset is not None:
            self["offset"] = offset
        if advanced is not None:
            self["advanced"] = advanced
        if additional_fields is not None:
            self.update(additional_fields)

    def set_query(self, query: str) -> "SearchQuery":
        self["q"] = query
        return self

    def set_limit(self, limit: int) -> "SearchQuery":
        self["limit"] = limit
        return self

    def set_offset(self, offset: int) -> "SearchQuery":
        self["offset"] = offset
        return self

    def set_advanced(self, advanced: bool) -> "SearchQuery":
        self["advanced"] = advanced
        return self

    def add_facet(
        self,
        name,
        field_name,
        type="terms",
        size=None,
        date_interval=None,
        histogram_range=None,
        **kwargs
    ) -> "SearchQuery":
        self["facets"] = self.get("facets", [])
        facet = {"name": name, "field_name": field_name, "type": type}
        facet.update(kwargs)
        if size is not None:
            facet["size"] = size
        if date_interval is not None:
            facet["date_interval"] = date_interval
        if histogram_range is not None:
            low, high = histogram_range
            facet["histogram_range"] = {"low": low, "high": high}
        self["facets"].append(facet)
        return self

    def add_filter(
        self, field_name, values, type="match_all", **kwargs
    ) -> "SearchQuery":
        self["filters"] = self.get("filters", [])
        new_filter = {"field_name": field_name, "values": values, "type": type}
        new_filter.update(kwargs)
        self["filters"].append(new_filter)
        return self

    def add_boost(self, field_name, factor, **kwargs) -> "SearchQuery":
        self["boosts"] = self.get("boosts", [])
        boost = {"field_name": field_name, "factor": factor}
        boost.update(kwargs)
        self["boosts"].append(boost)
        return self

    def add_sort(self, field_name, order=None, **kwargs) -> "SearchQuery":
        self["sort"] = self.get("sort", [])
        sort = {"field_name": field_name}
        sort.update(kwargs)
        if order is not None:
            sort["order"] = order
        self["sort"].append(sort)
        return self
