Changed
-------

- Passing non-``Scope`` types to ``Scope.with_dependency`` and
  ``Scope.with_dependencies`` now raises a ``TypeError``. Previously, this was
  allowed at runtime but created an invalid ``Scope`` object. (:pr:`NUMBER`)
