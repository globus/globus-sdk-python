Changed
~~~~~~~

- The client for Globus Timers has been renamed to ``TimersClient``. The prior
  name, ``TimerClient``, has been retained as an alias. (:pr:`NUMBER`)

  - Similarly, the error and scopes classes have been renamed and aliased:
    ``TimersAPIError`` replaces ``TimerAPIError`` and ``TimersScopes`` replaces
    ``TimerScopes``.

  - Internal module names have been changed to ``timers`` from ``timer`` where
    possible.

  - The ``service_name`` attribute is left as ``timer`` for now, as it is
    integrated into URL and ``_testing`` logic.


Deprecated
~~~~~~~~~~

- ``TimerScopes`` is now a deprecated name. Use ``TimersScopes`` instead. (:pr:`NUMBER`)

Documentation
~~~~~~~~~~~~~

- The Globus Timers examples have been significantly enhanced and now leverage
  more modern usage patterns. (:pr:`NUMBER`)
