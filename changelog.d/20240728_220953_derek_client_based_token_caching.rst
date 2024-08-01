
Changed
~~~~~~~

-   Changed the experimental ``GlobusApp`` class in the following way (:pr:`NUMBER`):

    -   ``app_name`` is no longer required (defaults to "DEFAULT")

    -   Token storage now defaults to including the client id in the path.

        -   Old (unix) : ``~/.globus/app/{app_name}/tokens.json``

        -   New (unix): ``~/.globus/app/{client_id}/{app_name}/tokens.json``

        -   Old (win): ``~\AppData\Local\globus\app\{app_name}\tokens.json``

        -   New (win): ``~\AppData\Local\globus\app\{client_id}\{app_name}\tokens.json``

    -   ``GlobusAppConfig.token_storage`` now accepts shorthand string references:
        ``"json"`` to use a ``JSONTokenStorage``, ``"sqlite"`` to use a
        ``SQLiteTokenStorage`` and ``"memory"`` to use a ``MemoryTokenStorage``.

    -   ``GlobusAppConfig.token_storage`` also now accepts a ``TokenStorageProvider``,
        a class with a ``for_globus_app(...) -> TokenStorage`` class method.

    -   Renamed the experimental ``FileTokenStorage`` attribute ``.filename`` to
        ``.filepath``.
