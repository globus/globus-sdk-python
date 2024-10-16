from __future__ import annotations

import typing as t

from globus_sdk import exc, utils

# workaround for absence of Self type
# for the workaround and some background, see:
#   https://github.com/python/mypy/issues/11871
SearchQueryT = t.TypeVar("SearchQueryT", bound="SearchQueryBase")


# an internal class for declaring multiple related types with shared methods
class SearchQueryBase(utils.PayloadWrapper):
    """
    The base class for all Search query helpers.

    Search has multiple types of query documents. Not all of their supported attributes
    are shared, and they therefore do not inherit from one another.
    This class implements common methods to all of them.

    Query objects have a chainable API, in which methods return the query object after
    modification. This allows usage like

    >>> query = ...
    >>> query = query.set_limit(10).set_advanced(False)
    """

    def set_query(self: SearchQueryT, query: str) -> SearchQueryT:
        """
        Set the query string for the query document.

        :param query: the new query string
        """
        self["q"] = query
        return self

    def set_limit(self: SearchQueryT, limit: int) -> SearchQueryT:
        """
        Set the limit for the query document.

        :param limit: a limit on the number of results returned in a single page
        """
        self["limit"] = limit
        return self

    def set_advanced(self: SearchQueryT, advanced: bool) -> SearchQueryT:
        """
        Enable or disable advanced query string processing.

        :param advanced: whether to enable (``True``) or not (``False``)
        """
        self["advanced"] = advanced
        return self

    def add_filter(
        self: SearchQueryT,
        field_name: str,
        values: list[str],
        *,
        # pylint: disable=redefined-builtin
        type: str = "match_all",
        additional_fields: dict[str, t.Any] | None = None,
    ) -> SearchQueryT:
        """
        Add a filter subdocument to the query.

        :param field_name: the field on which to filter
        :param values: the values to use in the filter
        :param type: the type of filter to apply, defaults to "match_all"
        :param additional_fields: additional data to include in the filter document
        """
        self["filters"] = self.get("filters", [])
        new_filter = {
            "field_name": field_name,
            "values": values,
            "type": type,
            **(additional_fields or {}),
        }
        self["filters"].append(new_filter)
        return self


class SearchQuery(SearchQueryBase):
    """
    A specialized dict which has helpers for creating and modifying a Search
    Query document.

    :param q: The query string. Required unless filters are used.
    :param limit: A limit on the number of results returned in a single page
    :param offset: An offset into the set of all results for the query
    :param advanced: Whether to enable (``True``) or not to enable (``False``) advanced
        parsing of query strings. The default of ``False`` is robust and guarantees that
        the query will not error with "bad query string" errors
    :param additional_fields: additional data to include in the query document

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
        q: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        advanced: bool | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ):
        super().__init__()
        exc.warn_deprecated("'SearchQuery' is deprecated. Use 'SearchQueryV1' instead.")
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

    def set_offset(self, offset: int) -> SearchQuery:
        """
        Set the offset for the query document.

        :param offset: an offset into the set of all results for the query
        """
        self["offset"] = offset
        return self

    def add_facet(
        self,
        name: str,
        field_name: str,
        *,
        # pylint: disable=redefined-builtin
        type: str = "terms",
        size: int | None = None,
        date_interval: str | None = None,
        histogram_range: tuple[t.Any, t.Any] | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> SearchQuery:
        """
        Add a facet subdocument to the query.

        :param name: the name for the facet in the result
        :param field_name: the field on which to build the facet
        :param type: the type of facet to apply, defaults to "terms"
        :param size: the size parameter for the facet
        :param date_interval: the date interval for a date histogram facet
        :param histogram_range: a low and high bound for a numeric histogram facet
        :param additional_fields: additional data to include in the facet document
        """
        self["facets"] = self.get("facets", [])
        facet: dict[str, t.Any] = {
            "name": name,
            "field_name": field_name,
            "type": type,
            **(additional_fields or {}),
        }
        if size is not None:
            facet["size"] = size
        if date_interval is not None:
            facet["date_interval"] = date_interval
        if histogram_range is not None:
            low, high = histogram_range
            facet["histogram_range"] = {"low": low, "high": high}
        self["facets"].append(facet)
        return self

    def add_boost(
        self,
        field_name: str,
        factor: str | int | float,
        *,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> SearchQuery:
        """
        Add a boost subdocument to the query.

        :param field_name: the field to boost in result weighting
        :param factor: the factor by which to adjust the field weight (where ``1.0`` is
            the default weight)
        :param additional_fields: additional data to include in the boost document
        """
        self["boosts"] = self.get("boosts", [])
        boost = {
            "field_name": field_name,
            "factor": factor,
            **(additional_fields or {}),
        }
        self["boosts"].append(boost)
        return self

    def add_sort(
        self,
        field_name: str,
        *,
        order: str | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ) -> SearchQuery:
        """
        Add a sort subdocument to the query.

        :param field_name: the field on which to sort
        :param order: ascending or descending order, given as ``"asc"`` or ``"desc"``
        :param additional_fields: additional data to include in the sort document
        """
        self["sort"] = self.get("sort", [])
        sort = {"field_name": field_name, **(additional_fields or {})}
        if order is not None:
            sort["order"] = order
        self["sort"].append(sort)
        return self


class SearchQueryV1(utils.PayloadWrapper):
    """
    A specialized dict which has helpers for creating and modifying a Search
    Query document. Replaces the usage of ``SearchQuery``.

    :param q: The query string. Required unless filters are used.
    :param limit: A limit on the number of results returned in a single page
    :param offset: An offset into the set of all results for the query
    :param advanced: Whether to enable (``True``) or not to enable (``False``) advanced
        parsing of query strings. The default of ``False`` is robust and guarantees that
        the query will not error with "bad query string" errors
    :param filters: a list of filters to apply to the query
    :param facets: a list of facets to apply to the query
    :param post_facet_filters: a list of filters to apply after facet
        results are returned
    :param boosts: a list of boosts to apply to the query
    :param sort: a list of fields to sort results
    :param additional_fields: additional data to include in the query document
    """

    def __init__(
        self,
        *,
        q: str | utils.MissingType = utils.MISSING,
        limit: int | utils.MissingType = utils.MISSING,
        offset: int | utils.MissingType = utils.MISSING,
        advanced: bool | utils.MissingType = utils.MISSING,
        filters: list[dict[str, t.Any]] | utils.MissingType = utils.MISSING,
        facets: list[dict[str, t.Any]] | utils.MissingType = utils.MISSING,
        post_facet_filters: list[dict[str, t.Any]] | utils.MissingType = utils.MISSING,
        boosts: list[dict[str, t.Any]] | utils.MissingType = utils.MISSING,
        sort: list[dict[str, t.Any]] | utils.MissingType = utils.MISSING,
        additional_fields: dict[str, t.Any] | utils.MissingType = utils.MISSING,
    ):
        super().__init__()
        self["@version"] = "query#1.0.0"

        self["q"] = q
        self["limit"] = limit
        self["offset"] = offset
        self["advanced"] = advanced
        self["filters"] = filters
        self["facets"] = facets
        self["post_facet_filters"] = post_facet_filters
        self["boosts"] = boosts
        self["sort"] = sort

        if not isinstance(additional_fields, utils.MissingType):
            self.update(additional_fields)


class SearchScrollQuery(SearchQueryBase):
    """
    A scrolling query type, for scrolling the full result set for an index.

    Scroll queries have more limited capabilities than general searches.
    They cannot boost fields, sort, or apply facets. They can, however, still apply the
    same filtering mechanisms which are available to normal queries.

    Scrolling also differs in that it supports the use of the ``marker`` field, which is
    used to paginate results.

    :param q: The query string
    :param limit: A limit on the number of results returned in a single page
    :param advanced: Whether to enable (``True``) or not to enable (``False``) advanced
        parsing of query strings. The default of ``False`` is robust and guarantees that
        the query will not error with "bad query string" errors
    :param marker: the marker value
    :param additional_fields: additional data to include in the query document
    """

    def __init__(
        self,
        q: str | None = None,
        *,
        limit: int | None = None,
        advanced: bool | None = None,
        marker: str | None = None,
        additional_fields: dict[str, t.Any] | None = None,
    ):
        super().__init__()
        if q is not None:
            self["q"] = q
        if limit is not None:
            self["limit"] = limit
        if advanced is not None:
            self["advanced"] = advanced
        if marker is not None:
            self["marker"] = marker
        if additional_fields is not None:
            self.update(additional_fields)

    def set_marker(self, marker: str) -> SearchScrollQuery:
        """
        Set the marker on a scroll query.

        :param marker: the marker value
        """
        self["marker"] = marker
        return self
