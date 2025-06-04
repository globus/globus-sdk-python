Changed
~~~~~~~

- ``Scope`` objects are now immutable, and their internal ``dependencies`` are
  held in a tuple. (:pr:`NUMBER`)

  - The ``add_dependency`` method has been removed, since mutating a ``Scope``
    is no longer possible.

  - A new evolver method, ``Scope.with_dependency`` has been added. It extends
    the ``dependencies`` tuple in a new ``Scope`` object.

  - A batch version of ``Scope.with_dependency`` has been added,
    ``Scope.with_dependencies``.

  - An evolver for the ``optional`` field of a ``Scope`` is also now available,
    as ``Scope.with_optional``.
