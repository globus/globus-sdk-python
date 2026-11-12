Deprecated
----------

- ``FileTokenStorage.user_only_umask()`` and ``FileAdapter.user_only_umask()``
  are deprecated and will be removed in version 5. (:pr:`1449`)

  They change the umask of the whole process,
  which is not safe when other threads are running.

Fixed
-----

- All file-based token storage classes create files
  with mode ``0o600`` set directly, and do not change the process umask. (:pr:`1449`)

  This avoids a thread safety issue that could cause I/O in other threads
  to create files with an unexpected umask.
