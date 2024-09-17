from __future__ import annotations

import json
import pathlib
import sqlite3
import textwrap
import typing as t

from globus_sdk import exc
from globus_sdk.experimental.tokenstorage.base import FileTokenStorage
from globus_sdk.version import __version__

from .token_data import TokenStorageData


class SQLiteTokenStorage(FileTokenStorage):
    """
    A storage adapter for storing token data in sqlite databases.

    SQLite adapters are for more complex cases, where there may be multiple users or
    "profiles" in play, and additionally a dynamic set of resource servers which need to
    be stored in an extensible way.

    The ``connect_params`` is an optional dictionary whose elements are passed directly
    to the underlying ``sqlite3.connect()`` method, enabling developers to fine-tune the
    connection to the SQLite database.  Refer to the ``sqlite3.connect()``
    documentation for SQLite-specific parameters.
    """

    file_format = "db"

    def __init__(
        self,
        filepath: pathlib.Path | str,
        *,
        connect_params: dict[str, t.Any] | None = None,
        namespace: str = "DEFAULT",
    ) -> None:
        """
        :param filepath: The path of the DB file to write to and read from.
        :param connect_params: A pass-through dictionary for fine-tuning the SQLite
             connection.
        :param namespace: A user-supplied namespace for partitioning token data.
        """
        if filepath == ":memory:":
            raise exc.GlobusSDKUsageError(
                "SQLiteTokenStorage cannot be used with a ':memory:' database. "
                "If you want to store tokens in memory, use MemoryTokenStorage instead."
            )

        super().__init__(filepath, namespace=namespace)
        self._connection = self._init_and_connect(connect_params)

    def _init_and_connect(
        self,
        connect_params: dict[str, t.Any] | None,
    ) -> sqlite3.Connection:
        connect_params = connect_params or {}
        if not self.file_exists():
            with self.user_only_umask():
                conn: sqlite3.Connection = sqlite3.connect(
                    self.filepath, **connect_params
                )
            conn.executescript(
                textwrap.dedent(
                    """
                    CREATE TABLE token_storage (
                        namespace VARCHAR NOT NULL,
                        resource_server VARCHAR NOT NULL,
                        token_data_json VARCHAR NOT NULL,
                        PRIMARY KEY (namespace, resource_server)
                    );
                    CREATE TABLE sdk_storage_adapter_internal (
                        attribute VARCHAR NOT NULL,
                        value VARCHAR NOT NULL,
                        PRIMARY KEY (attribute)
                    );
                    """
                )
            )
            # mark the version which was used to create the DB
            # also mark the "database schema version" in case we ever need to handle
            # graceful upgrades
            conn.executemany(
                "INSERT INTO sdk_storage_adapter_internal(attribute, value) "
                "VALUES (?, ?)",
                [
                    ("globus-sdk.version", __version__),
                    # schema_version=1 indicates a schema built with the original
                    # SQLiteAdapter
                    # schema_version=2 indicates one built with SQLiteTokenStorage
                    #
                    # a schema_version of 1 therefore indicates that there should be
                    # a 'config_storage' table present
                    ("globus-sdk.database_schema_version", "2"),
                ],
            )
            conn.commit()
        else:
            conn = sqlite3.connect(self.filepath, **connect_params)
        return conn

    def close(self) -> None:
        """
        Close the underlying database connection.
        """
        self._connection.close()

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        Given a dict of token data indexed by resource server, convert the data into
        JSON dicts and write it to ``self.filepath`` under the current namespace

        :param token_data_by_resource_server: a ``dict`` of ``TokenStorageData`` objects
            indexed by their ``resource_server``.
        """
        pairs = []
        for resource_server, token_data in token_data_by_resource_server.items():
            pairs.append((resource_server, token_data.to_dict()))

        self._connection.executemany(
            "REPLACE INTO token_storage(namespace, resource_server, token_data_json) "
            "VALUES(?, ?, ?)",
            [
                (self.namespace, rs_name, json.dumps(token_data_dict))
                for (rs_name, token_data_dict) in pairs
            ],
        )
        self._connection.commit()

    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        """
        Lookup all token data under the current namespace from the database.

        Returns a dict of ``TokenStorageData`` objects indexed by their resource server.
        """
        ret: dict[str, TokenStorageData] = {}
        for row in self._connection.execute(
            "SELECT resource_server, token_data_json "
            "FROM token_storage WHERE namespace=?",
            (self.namespace,),
        ):
            resource_server, token_data_json = row
            token_data_dict = json.loads(token_data_json)
            ret[resource_server] = TokenStorageData.from_dict(token_data_dict)
        return ret

    def remove_token_data(self, resource_server: str) -> bool:
        """
        Given a resource server to target, delete token data for that resource server
        from the database (limited to the current namespace).
        You can use this as part of a logout command implementation, loading token data
        as a dict, and then deleting the data for each resource server.

        Returns True if token data was deleted, False if none was found to delete.

        :param resource_server: The name of the resource server to remove from the DB
        """
        rowcount = self._connection.execute(
            "DELETE FROM token_storage WHERE namespace=? AND resource_server=?",
            (self.namespace, resource_server),
        ).rowcount
        self._connection.commit()
        return rowcount != 0

    def iter_namespaces(self) -> t.Iterator[str]:
        """
        Iterate over the namespaces which are in use in this storage adapter's database.
        The presence of tokens for a namespace does not indicate that those tokens are
        valid, only that they have been stored and have not been removed.
        """
        seen: set[str] = set()
        for row in self._connection.execute(
            "SELECT DISTINCT namespace FROM token_storage;"
        ):
            namespace = row[0]
            seen.add(namespace)
            yield namespace
