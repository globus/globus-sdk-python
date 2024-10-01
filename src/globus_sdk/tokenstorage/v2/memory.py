from __future__ import annotations

import typing as t

from .base import TokenStorage
from .token_data import TokenStorageData

if t.TYPE_CHECKING:
    from globus_sdk._types import UUIDLike
    from globus_sdk.globus_app import GlobusAppConfig


class MemoryTokenStorage(TokenStorage):
    """
    A token storage which holds tokens in-memory.
    All token data is lost when the process exits.

    See :class:`TokenStorage` for common interface details.

    :param namespace: A unique string for partitioning token data (Default: "DEFAULT").
    """

    def __init__(self, *, namespace: str = "DEFAULT") -> None:
        self._tokens: dict[str, dict[str, t.Any]] = {}
        super().__init__(namespace=namespace)

    @classmethod
    def for_globus_app(
        cls,
        # pylint: disable=unused-argument
        client_id: UUIDLike,
        app_name: str,
        config: GlobusAppConfig,
        # pylint: enable=unused-argument
        namespace: str,
    ) -> MemoryTokenStorage:
        return cls(namespace=namespace)

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        if self.namespace not in self._tokens:
            self._tokens[self.namespace] = {}

        for resource_server, token_data in token_data_by_resource_server.items():
            self._tokens[self.namespace][resource_server] = token_data.to_dict()

    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        ret = {}
        dicts_by_resource_server = self._tokens.get(self.namespace, {})
        for resource_server, token_data_dict in dicts_by_resource_server.items():
            ret[resource_server] = TokenStorageData.from_dict(token_data_dict)
        return ret

    def remove_token_data(self, resource_server: str) -> bool:
        popped = self._tokens.get(self.namespace, {}).pop(resource_server, None)
        return popped is not None
