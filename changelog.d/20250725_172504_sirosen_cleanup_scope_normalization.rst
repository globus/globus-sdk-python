Breaking Changes
----------------

- Interfaces for normalizing scope data have changed. (:pr:`NUMBER`)

  - The ``scopes_to_str`` function has been replaced with
    ``ScopeParser.serialize``.

  - ``ScopeParser.serialize`` will raise an error if the serialized data is
    empty. A flag, ``reject_empty=False``, can be passed to disable this check.

  - The ``scopes_to_scope_list`` function has been removed.
