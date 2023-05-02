* ``ConsentRequiredInfo`` now accepts ``required_scope`` (singular) containing
  a single string as an alternative to ``required_scopes``. However, it will
  parse both formats into a ``required_scopes`` list. (:pr:`NUMBER`)
