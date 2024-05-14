from __future__ import annotations

import typing as t

from globus_sdk.experimental.tokenstorage.base import TokenStorage

from .token_data import TokenData


class MemoryTokenStorage(TokenStorage):
    """
    A token storage adapter which stores token data in process memory.

    Tokens are lost when the process exits.
    """

    def __init__(self, *, namespace: str = "DEFAULT") -> None:
        self._tokens: dict[str, dict[str, t.Any]] = {}
        super().__init__(namespace=namespace)

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        if self.namespace not in self._tokens:
            self._tokens[self.namespace] = {}

        for resource_server, token_data in token_data_by_resource_server.items():
            self._tokens[self.namespace][resource_server] = token_data.to_dict()

    def get_token_data_by_resource_server(self) -> dict[str, TokenData]:
        ret = {}
        dicts_by_resource_server = self._tokens.get(self.namespace, {})
        for resource_server, token_data_dict in dicts_by_resource_server.items():
            ret[resource_server] = TokenData.from_dict(token_data_dict)
        return ret

    def remove_token_data(self, resource_server: str) -> bool:
        popped = self._tokens.get(self.namespace, {}).pop(resource_server, None)
        return popped is not None
