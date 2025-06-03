Changed
~~~~~~~

- Scope parsing has been separated from the main ``Scope`` class into a
  dedicated ``ScopeParser`` which provides parsing methods. (:pr:`NUMBER`)

  - Use ``globus_sdk.scopes.ScopeParser`` for complex parsing use-cases. The
    ``ScopeParser.parse`` classmethod parses strings into lists of scope
    objects.

  - ``Scope.serialize`` and ``Scope.deserialize`` have been removed as methods.

  - ``Scope.parse`` is changed to call ``ScopeParser.parse`` and verify that
    there is exactly one result, which it returns. This means that
    ``Scope.parse`` now returns a single ``Scope``, not a ``list[Scope]``.

  - ``Scope.merge_scopes`` has been moved to ``ScopeParser.merge_scopes``.
