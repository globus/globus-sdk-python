* Improvements to ``MutableScope`` objects (:pr:`NUMBER`)

  * ``MutableScope(...).serialize()`` is added, and ``str(MutableScope(...))`` uses it

  * ``MutableScope.add_dependency`` now supports ``MutableScope`` objects as inputs

  * The ``optional`` argument to ``add_dependency`` is deprecated.
    ``MutableScope(...).add_dependency(MutableScope("foo", optional=True))``
    can be used to add an optional dependency

  * ``ScopeBuilder.make_mutable`` now accepts a keyword argument ``optional``.
    This allows, for example, ``TransferScopes.make_mutable("all", optional=True)``
