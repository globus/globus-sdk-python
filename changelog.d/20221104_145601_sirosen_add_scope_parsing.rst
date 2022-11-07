* Enhance scope utilities with scope parsing, attached to
  ``globus_sdk.scopes.Scope`` (:pr:`NUMBER`)

  * ``MutableScope`` has been renamed to ``Scope``. Both names remain available
    for backwards compatibility, but the preferred name is now ``Scope``

  * ``Scope.parse`` and ``Scope.deserialize`` can now be used to parse strings
    into ``Scope``\s

  * ``Scope(...).serialize()`` is added, and ``str(Scope(...))`` uses it

  * ``Scope.add_dependency`` now supports ``Scope`` objects as inputs

  * The ``optional`` argument to ``add_dependency`` is deprecated.
    ``Scope(...).add_dependency("*foo")`` can be used to add an optional
    dependency as a string, or equivalently
    ``Scope(...).add_dependency(Scope("foo", optional=True))``

  * ``Scope``\s support permission coverage checking with the ``in`` and
    ``not in`` operators. ``scope1 in scope2`` means that a token issued for
    ``scope2`` has all of the permissions of a token issued for ``scope1``. The
    check therefore can be used to validate that an existing token has the
    permissions associated with a prospective request.

  * ``ScopeBuilder.make_mutable`` now accepts a keyword argument ``optional``.
    This allows, for example,
    ``TransferScopes.make_mutable("all", optional=True)``
