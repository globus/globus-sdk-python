Changed
~~~~~~~

- ``session_required_policies`` parsing in ``AuthorizationParameterInfo`` now
  supports the policies being returned as a ``list[str]`` in addition to
  supporting ``str`` (:pr:`NUMBER`)

Fixed
~~~~~

- ``AuthorizationParameterInfo`` is now more type-safe, and will not return
  parsed data from a response without checking that the data has correct types
  (:pr:`NUMBER`)
