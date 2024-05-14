from __future__ import annotations

import json
import pathlib
import sqlite3
import textwrap
import typing as t

from globus_sdk.experimental.tokenstorage.base import FileTokenStorage
from globus_sdk.version import __version__

from .token_data import TokenData


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

    def __init__(
        self,
        dbname: pathlib.Path | str,
        *,
        connect_params: dict[str, t.Any] | None = None,
        namespace: str = "DEFAULT",
    ):
        """
        :param dbname: The name of the DB file to write to and read from. If the string
            ":memory:" is used, an in-memory database will be used instead.
        :param connect_params: A pass-through dictionary for fine-tuning the SQLite
             connection.
        :param namespace: A user-supplied namespace for partitioning token data.
        """
        self.filename = self.dbname = str(dbname)
        self._connection = self._init_and_connect(connect_params)
        super().__init__(namespace=namespace)

    def _is_memory_db(self) -> bool:
        return self.dbname == ":memory:"

    def _init_and_connect(
        self,
        connect_params: dict[str, t.Any] | None,
    ) -> sqlite3.Connection:
        init_tables = self._is_memory_db() or not self.file_exists()
        connect_params = connect_params or {}
        if init_tables and not self._is_memory_db():  # real file needs to be created
            with self.user_only_umask():
                conn = sqlite3.connect(self.dbname, **connect_params)
        else:
            conn = sqlite3.connect(self.dbname, **connect_params)
        if init_tables:
            conn.executescript(
                textwrap.dedent(
                    """
                    CREATE TABLE config_storage (
                        namespace VARCHAR NOT NULL,
                        config_name VARCHAR NOT NULL,
                        config_data_json VARCHAR NOT NULL,
                        PRIMARY KEY (namespace, config_name)
                    );
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
                    ("globus-sdk.database_schema_version", "1"),
                ],
            )
            conn.commit()
        return conn

    def close(self) -> None:
        """
        Close the underlying database connection.
        """
        self._connection.close()

    def store_config(
        self, config_name: str, config_dict: t.Mapping[str, t.Any]
    ) -> None:
        """
        Store a config dict under the current namespace in the config table.
        Allows arbitrary configuration data to be namespaced under the namespace, so
        that application config may be associated with the stored token data.

        Uses sqlite "REPLACE" to perform the operation.

        :param config_name: A string name for the configuration value
        :param config_dict: A dict of config which will be stored serialized as JSON
        """
        self._connection.execute(
            "REPLACE INTO config_storage(namespace, config_name, config_data_json) "
            "VALUES (?, ?, ?)",
            (self.namespace, config_name, json.dumps(config_dict)),
        )
        self._connection.commit()

    def read_config(self, config_name: str) -> dict[str, t.Any] | None:
        """
        Load a config dict under the current namespace in the config table.
        If no value is found, returns None

        :param config_name: A string name for the configuration value
        """
        row = self._connection.execute(
            "SELECT config_data_json FROM config_storage "
            "WHERE namespace=? AND config_name=?",
            (self.namespace, config_name),
        ).fetchone()

        if row is None:
            return None
        config_data_json = row[0]
        val = json.loads(config_data_json)
        if not isinstance(val, dict):
            raise ValueError("reading config data and got non-dict result")
        return val

    def remove_config(self, config_name: str) -> bool:
        """
        Delete a previously stored configuration value.

        Returns True if data was deleted, False if none was found to delete.

        :param config_name: A string name for the configuration value
        """
        rowcount = self._connection.execute(
            "DELETE FROM config_storage WHERE namespace=? AND config_name=?",
            (self.namespace, config_name),
        ).rowcount
        self._connection.commit()
        return rowcount != 0

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        """
        Given a dict of token data indexed by resource server, convert the data into
        JSON dicts and write it to ``self.dbname`` under the current namespace

        :param token_data_by_resource_server: a ``dict`` of ``TokenData`` objects
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

    def get_token_data_by_resource_server(self) -> dict[str, TokenData]:
        """
        Lookup all token data under the current namespace from the database.

        Returns a dict of ``TokenData`` objects indexed by their resource server.
        """
        ret: dict[str, TokenData] = {}
        for row in self._connection.execute(
            "SELECT resource_server, token_data_json "
            "FROM token_storage WHERE namespace=?",
            (self.namespace,),
        ):
            resource_server, token_data_json = row
            token_data_dict = json.loads(token_data_json)
            ret[resource_server] = TokenData.from_dict(token_data_dict)
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

    def iter_namespaces(
        self, *, include_config_namespaces: bool = False
    ) -> t.Iterator[str]:
        """
        Iterate over the namespaces which are in use in this storage adapter's database.
        The presence of tokens for a namespace does not indicate that those tokens are
        valid, only that they have been stored and have not been removed.

        :param include_config_namespaces: Include namespaces which appear only in the
            configuration storage section of the sqlite database. By default, only
            namespaces which were used for token storage will be returned
        """
        seen: set[str] = set()
        for row in self._connection.execute(
            "SELECT DISTINCT namespace FROM token_storage;"
        ):
            namespace = row[0]
            seen.add(namespace)
            yield namespace

        if include_config_namespaces:
            for row in self._connection.execute(
                "SELECT DISTINCT namespace FROM config_storage;"
            ):
                namespace = row[0]
                if namespace not in seen:
                    yield namespace
