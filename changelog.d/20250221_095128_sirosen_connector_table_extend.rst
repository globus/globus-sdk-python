Added
~~~~~

- ``ConnectorTable`` has a new classmethod, ``extend`` which allows users to
  add new connectors to the mapping. ``ConnectorTable.extend()`` returns a new
  connector table subclass and does not modify the original. (:pr:`NUMBER`)
