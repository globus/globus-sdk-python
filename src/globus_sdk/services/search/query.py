class SearchQuery(dict):
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

    def set_query(self, query):
        self["q"] = query
        return self

    def set_limit(self, limit):
        self["limit"] = limit
        return self

    def set_offset(self, offset):
        self["offset"] = offset
        return self

    def set_advanced(self, advanced):
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
    ):
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

    def add_filter(self, field_name, values, type="match_all", **kwargs):
        self["filters"] = self.get("filters", [])
        new_filter = {"field_name": field_name, "values": values, "type": type}
        new_filter.update(kwargs)
        self["filters"].append(new_filter)
        return self

    def add_boost(self, field_name, factor, **kwargs):
        self["boosts"] = self.get("boosts", [])
        boost = {"field_name": field_name, "factor": factor}
        boost.update(kwargs)
        self["boosts"].append(boost)
        return self

    def add_sort(self, field_name, order=None, **kwargs):
        self["sort"] = self.get("sort", [])
        sort = {"field_name": field_name}
        sort.update(kwargs)
        if order is not None:
            sort["order"] = order
        self["sort"].append(sort)
        return self
