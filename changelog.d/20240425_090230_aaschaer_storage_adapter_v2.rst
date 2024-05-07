Added
~~~~~

- Added ``TokenStorage`` to experimental along with ``FileTokenStorage``,
    ``JSONTokenStorage``, ``MemoryTokenStorage`` and ``SQLiteTokenStorage`` which
    implement it. ``TokenStorage`` expands the functionality of ``StorageAdapter``
    but is not fully backwards compatible. (:pr:`NUMBER`)

Changed
~~~~~~~

- The experimental class ``ValidatingStorageAdapater`` has been renamed to
  ``ValidatingTokenStorage`` and now implements ``TokenStorage`` instead of
  ``StorageAdapter`` (:pr:`NUMBER`)
