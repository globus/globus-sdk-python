from __future__ import annotations

import typing as t
from urllib.parse import parse_qs, urlsplit

from .base import PageT, Paginator


class JSONAPIPaginator(Paginator[PageT]):
    """
    A paginator which uses the next link of a JSON:API response if present
    to fetch more pages.

    Assumes the next link only changes query parameters between calls to
    `method` and that `method` supports a keyword argument of `query_params`
    which those changed query parameters will be passed to.
    """

    _REQUIRES_METHOD_KWARGS = ("get_method",)

    def _get_next_link(self, page: dict[str, t.Any]) -> str | None:
        links = page.get("links")
        if links:
            next_link = links.get("next")
            if isinstance(next_link, str):
                return next_link
        return None

    def pages(self) -> t.Iterator[PageT]:
        while True:
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page

            next_link = self._get_next_link(current_page)
            if next_link:
                next_link_query_params = parse_qs(urlsplit(next_link).query)
                self.client_kwargs["query_params"] = next_link_query_params
            else:
                break
