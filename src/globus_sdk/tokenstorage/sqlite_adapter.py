import json
import sqlite3
from typing import Any, Dict, Iterator, Mapping, Optional, Set

from globus_sdk.services.auth import OAuthTokenResponse
from globus_sdk.tokenstorage.base import FileAdapter
from globus_sdk.version import __version__


class SQLiteAdapter(FileAdapter):
    """
    :param dbname: The name of the DB file to write to and read from. If the string
        ":memory:" is used, an in-memory database will be used instead.
    :type dbname: str
    :param namespace: A "namespace" to use within the database. All operations will
        be performed indexed under this string, so that multiple distinct sets of tokens
        may be stored in the database. You might use usernames as the namespace to
        implement a multi-user system, or profile names to allow multiple Globus
        accounts to be used by a single user.
    :type namespace: str, optional
    :param connect_params: A pass-through dictionary for fine-tuning the SQLite
         connection.
    :type connect_params: dict, optional

    A storage adapter for storing tokens in sqlite databases.

    SQLite adapters are for more complex cases, where there may be multiple users or
    "profiles" in play, and additionally a dynamic set of resource servers which need to
    be stored in an extensible way.

    The ``namespace`` is a user-supplied way of partitioning data, and any token
    responses passed to the storage adapter are broken apart and stored indexed by
    *resource_server*. If you have a more complex use-case in which this scheme will be
    insufficient, you should encode that in your choice of ``namespace`` values.

    The ``connect_params`` is an optional dictionary whose elements are passed directly
    to the underlying ``sqlite3.connect()`` method, enabling developers to fine-tune the
    connection to the SQLite database.  Refer to the ``sqlite3.connect()``
    documentation for SQLite-specific parameters.
    """

    def __init__(
        self,
        dbname: str,
        *,
        namespace: str = "DEFAULT",
        connect_params: Optional[Dict[str, Any]] = None
    ):
        self.filename = self.dbname = dbname
        self.namespace = namespace
        self._connection = self._init_and_connect(connect_params)

    def _is_memory_db(self) -> bool:
        return self.dbname == ":memory:"

    def _init_and_connect(
        self,
        connect_params: Optional[Dict[str, Any]],
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

    def store_config(self, config_name: str, config_dict: Mapping[str, Any]) -> None:
        """
        :param config_name: A string name for the configuration value
        :type config_name: str
        :param config_dict: A dict of config which will be stored serialized as JSON
        :type config_dict: Mapping

        Store a config dict under the current namespace in the config table.
        Allows arbitrary configuration data to be namespaced under the namespace, so
        that application config may be associated with the stored tokens.

        Uses sqlite "REPLACE" to perform the operation.
        """
        self._connection.execute(
            "REPLACE INTO config_storage(namespace, config_name, config_data_json) "
            "VALUES (?, ?, ?)",
            (self.namespace, config_name, json.dumps(config_dict)),
        )
        self._connection.commit()

    def read_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        :param config_name: A string name for the configuration value
        :type config_name: str

        Load a config dict under the current namespace in the config table.
        If no value is found, returns None
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
        :param config_name: A string name for the configuration value
        :type config_name: str

        Delete a previously stored configuration value.

        Returns True if data was deleted, False if none was found to delete.
        """
        rowcount = self._connection.execute(
            "DELETE FROM config_storage WHERE namespace=? AND config_name=?",
            (self.namespace, config_name),
        ).rowcount
        self._connection.commit()
        return rowcount != 0

    def store(self, token_response: OAuthTokenResponse) -> None:
        """
        :param token_response: a globus_sdk.OAuthTokenResponse object containing token
                               data to store
        :type token_response: globus_sdk.OAuthTokenResponse

        By default, ``self.on_refresh`` is just an alias for this function.

        Given a token response, extract the token data for the resource servers and
        write it to ``self.dbname``, stored under the adapter's namespace
        """
        pairs = []
        for rs_name, token_data in token_response.by_resource_server.items():
            pairs.append((rs_name, token_data))

        self._connection.executemany(
            "REPLACE INTO token_storage(namespace, resource_server, token_data_json) "
            "VALUES(?, ?, ?)",
            [
                (self.namespace, rs_name, json.dumps(token_data))
                for (rs_name, token_data) in pairs
            ],
        )
        self._connection.commit()

    def get_token_data(self, resource_server: str) -> Optional[Dict[str, Any]]:
        """
        Load the token data JSON for a specific resource server.

        In the event that the server cannot be found in the DB, return None.

        :param resource_server: The name of a resource server to lookup in the DB, as
            one would use as a key in OAuthTokenResponse.by_resource_server
        :type resource_server: str
        """
        for row in self._connection.execute(
            "SELECT token_data_json FROM token_storage "
            "WHERE namespace=? AND resource_server=?",
            (self.namespace, resource_server),
        ):
            (token_data_json,) = row
            val = json.loads(token_data_json)
            if not isinstance(val, dict):
                raise ValueError("data error: token data was not saved as a dict")
            return val
        return None

    def get_by_resource_server(self) -> Dict[str, Any]:
        """
        Load the token data JSON and return the resulting dict objects, indexed by
        resource server.

        This should look identical to an OAuthTokenResponse.by_resource_server in format
        and content. (But it is not attached to a token response object.)
        """
        data = {}
        for row in self._connection.execute(
            "SELECT resource_server, token_data_json "
            "FROM token_storage WHERE namespace=?",
            (self.namespace,),
        ):
            resource_server, token_data_json = row
            data[resource_server] = json.loads(token_data_json)
        return data

    def remove_tokens_for_resource_server(self, resource_server: str) -> bool:
        """
        Given a resource server to target, delete tokens for that resource server from
        the database (limited to the current namespace).
        You can use this as part of a logout command implementation, loading token data
        as a dict, and then deleting the data for each resource server.

        Returns True if token data was deleted, False if none was found to delete.

        :param resource_server: The name of the resource server to remove from the DB,
            as one would use as a key in OAuthTokenResponse.by_resource_server
        :type resource_server: str
        """
        rowcount = self._connection.execute(
            "DELETE FROM token_storage WHERE namespace=? AND resource_server=?",
            (self.namespace, resource_server),
        ).rowcount
        self._connection.commit()
        return rowcount != 0

    def iter_namespaces(
        self, *, include_config_namespaces: bool = False
    ) -> Iterator[str]:
        """
        Iterate over the namespaces which are in use in this storage adapter's database.
        The presence of tokens for a namespace does not indicate that those tokens are
        valid, only that they have been stored and have not been removed.

        :param include_config_namespaces: Include namespaces which appear only in the
            configuration storage section of the sqlite database. By default, only
            namespaces which were used for token storage will be returned
        :type include_config_namespaces: bool, optional
        """
        seen: Set[str] = set()
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
