from __future__ import annotations

import typing as t

from globus_sdk.experimental.tokenstorage import TokenStorage, TokenStorageData


class IdentityIDReader:
    """
    An ``IdentityIDReader`` is an object which is capable of reading and recording the
    Identity ID associated with TokenStorageData.

    It can consume a ``TokenStorage`` or a mapping of ``TokenStorageData``s and use
    these data to populate an ``identity_id`` property which it provides.

    :ivar identity_id: The Identity ID which was last read from data. May be ``None``
        if no data has been provided yet.
    """

    def __init__(self) -> None:
        self.identity_id: str | None = None

    def read_token_storage(self, token_storage: TokenStorage) -> str | None:
        """
        Load the token data from a ``TokenStorage`` and use it to try to populate
        an ``identity_id`` value.

        Returns the ``identity_id`` value which was produced.

        :param token_storage: The token storage whose data is being read.

        :raises ValueError: if there is inconsistent ``identity_id`` information
        """
        # pull the token data from the token_storage if possible
        # if no data is found, this will result in an empty dict
        all_token_data = token_storage.get_token_data_by_resource_server()
        return self.read_token_data_by_resource_server(all_token_data)

    def read_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> str | None:
        """
        Read token data by resource server and set the ``identity_id`` based on this
        value.

        Returns the ``identity_id`` value which was produced.

        :param token_data_by_resource_server: The token data to read for identity_id.

        :raises ValueError: if there is inconsistent ``identity_id`` information
        """
        self.identity_id = _pure_read_token_data_by_resource_server(
            token_data_by_resource_server
        )
        return self.identity_id


def _pure_read_token_data_by_resource_server(
    token_data_by_resource_server: t.Mapping[str, TokenStorageData]
) -> str | None:
    token_data_identity_ids: set[str] = {
        token_data.identity_id
        for token_data in token_data_by_resource_server.values()
        if token_data.identity_id is not None
    }

    if len(token_data_identity_ids) == 0:
        return None
    elif len(token_data_identity_ids) == 1:
        return token_data_identity_ids.pop()
    else:
        raise ValueError(
            "token_data_by_resource_server contained TokenStorageData objects with "
            f"different identity_id values: {token_data_identity_ids}"
        )
