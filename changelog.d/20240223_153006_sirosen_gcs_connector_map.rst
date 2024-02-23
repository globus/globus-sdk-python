Added
~~~~~

- Add ``globus_sdk.ConnectorTable`` which provides information on supported
  Globus Connect Server connectors. This object maps names to IDs and vice
  versa. (:pr:`NUMBER`)

Deprecated
~~~~~~~~~~

- ``GCSClient.connector_id_to_name`` has been deprecated. Use
  ``ConnectorTable.lookup_by_id`` instead. (:pr:`NUMBER`)
