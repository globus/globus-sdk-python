from typing import Any, Callable, Dict, Iterator, List, Optional

from .base import PageT, Paginator


class MarkerPaginator(Paginator[PageT]):
    """
    A paginator which uses `has_next_page` and `marker` from payloads, sets the `marker`
    query param to page.

    This is the default method for GCS pagination, so it's very simple.
    """

    def __init__(
        self,
        method: Callable[..., Any],
        *,
        items_key: Optional[str] = None,
        marker_key: str = "marker",
        client_args: List[Any],
        client_kwargs: Dict[str, Any]
    ):
        super().__init__(
            method,
            items_key=items_key,
            client_args=client_args,
            client_kwargs=client_kwargs,
        )
        self.marker: Optional[str] = None
        self.marker_key = marker_key

    def _check_has_next_page(self, page: Dict[str, Any]) -> bool:
        return bool(page.get("has_next_page", False))

    def pages(self) -> Iterator[PageT]:
        has_next_page = True
        while has_next_page:
            if self.marker:
                self.client_kwargs["marker"] = self.marker
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.marker = current_page.get(self.marker_key)
            has_next_page = self._check_has_next_page(current_page)


class NullableMarkerPaginator(MarkerPaginator[PageT]):
    """
    A paginator which uses a ``marker`` from payloads and sets the ``marker`` query
    param to page.

    Unlike the base MarkerPaginator, it checks for a null marker to indicate an end to
    pagination. (vs an explicit has_next_page key)
    """

    def _check_has_next_page(self, page: Dict[str, Any]) -> bool:
        return page.get(self.marker_key) is not None
