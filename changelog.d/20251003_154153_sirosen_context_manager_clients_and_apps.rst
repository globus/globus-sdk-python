Added
-----

- ``GlobusApp`` and SDK client classes now support usage as context managers, and
  feature a new ``close()`` method to close internal resources.
  ``close()`` is automatically called on exit. (:pr:`NUMBER`)

  - In support of this, token storages now all feature a ``close()`` method,
    which does nothing in the default implementation.
    Previously, only storages with underlying resources to manage featured a
    ``close()`` method.

  - ``GlobusApp`` will close any token storage via ``close()`` if the token storage
    was created by the app on init. Explicitly created storages will not be closed
    and must be explicitly closed via their ``close()`` method.

  - Any class inheriting from ``BaseClient`` features ``close()``, which will
    close any transport object created during client construction.

  - Transports which are created explicitly will not be closed by their clients,
    and must be explicitly closed.
