from __future__ import annotations

import typing as t

from .base import PageT, Paginator


class LastKeyPaginator(Paginator[PageT]):
    def __init__(
        self,
        method: t.Callable[..., t.Any],
        *,
        items_key: str | None = None,
        client_args: list[t.Any],
        client_kwargs: dict[str, t.Any],
    ):
        super().__init__(
            method,
            items_key=items_key,
            client_args=client_args,
            client_kwargs=client_kwargs,
        )
        self.last_key: str | None = None

    def pages(self) -> t.Iterator[PageT]:
        has_next_page = True
        while has_next_page:
            if self.last_key:
                self.client_kwargs["last_key"] = self.last_key
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.last_key = current_page.get("last_key")
            has_next_page = current_page["has_next_page"]
