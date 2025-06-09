Changed
~~~~~~~

- ``Scope`` objects are now immutable. (:pr:`1208`)

  - ``Scope.dependencies`` is now a tuple, not a list.

  - The ``add_dependency`` method has been removed, since mutating a ``Scope``
    is no longer possible.

  - A new evolver method, ``Scope.with_dependency`` has been added. It extends
    the ``dependencies`` tuple in a new ``Scope`` object.

  - A batch version of ``Scope.with_dependency`` has been added,
    ``Scope.with_dependencies``.

  - An evolver for the ``optional`` field of a ``Scope`` is also now available,
    named ``Scope.with_optional``.

- Scope parsing has been separated from the main ``Scope`` class into a
  dedicated ``ScopeParser`` which provides parsing methods. (:pr:`1208`)

  - Use ``globus_sdk.scopes.ScopeParser`` for complex parsing use-cases. The
    ``ScopeParser.parse`` classmethod parses strings into lists of scope
    objects.

  - ``Scope.merge_scopes`` has been moved to ``ScopeParser.merge_scopes``.

  - ``Scope.parse`` is changed to call ``ScopeParser.parse`` and verify that
    there is exactly one result, which it returns. This means that
    ``Scope.parse`` now returns a single ``Scope``, not a ``list[Scope]``.

  - ``Scope.serialize`` and ``Scope.deserialize`` have been removed as methods.
    Use ``str(scope_object)`` as a replacement for ``serialize()`` and
    ``Scope.parse`` as a replacement for ``deserialize()``.
