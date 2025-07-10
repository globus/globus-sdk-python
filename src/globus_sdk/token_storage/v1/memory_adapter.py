from __future__ import annotations

import typing as t

import globus_sdk

from .base import StorageAdapter


class MemoryAdapter(StorageAdapter):
    """
    A token storage adapter which stores tokens in process memory.

    Tokens are lost when the process exits.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, dict[str, t.Any]] = {}

    def store(self, token_response: globus_sdk.OAuthTokenResponse) -> None:
        self._tokens.update(token_response.by_resource_server)

    def get_token_data(self, resource_server: str) -> dict[str, t.Any] | None:
        return self._tokens.get(resource_server)
