Changed
~~~~~~~

- The ``scopes`` class attribute of ``SpecificFlowClient`` is now specialized
  to ensure that type checkers will allow access to ``SpecificFlowClient``
  scopes and ``resource_server`` values without ``cast``\ing. The value used is
  a specialized stub which raises useful errors when class-based access is
  performed. The ``scopes`` instance attribute is unchanged. (:pr:`NUMBER`)
