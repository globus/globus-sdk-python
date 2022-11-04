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

  * ``Scope``\s support containment checking (``Scope("foo") in Scope("bar")``),
    which means that all of the consents for one scope are a strict subset of
    the consents of another scope. Containment is therefore an indication that
    the associated permissions of a token for a scope string are covered by
    the set of permissions associated with another scope string.
