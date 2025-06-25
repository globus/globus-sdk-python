Changed
-------

- The ``ScopeBuilder`` types have been simplified and improved as the new
  ``ScopeCollection`` types. (:pr:`NUMBER`)

  - ``ScopeBuilder`` is replaced with ``StaticScopeCollection`` and
    ``DynamicScopeCollection``. The ``scopes`` attribute of client classes is
    now a scope collection.

  - The attributes of ``ScopeCollection``\s are ``Scope`` objects, not strings.

  - ``ScopeCollection``\s define ``__iter__``, yielding the provided scopes,
    but not ``__str__``.
