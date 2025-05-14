Breaking Changes
~~~~~~~~~~~~~~~~

- ``TimersAPIError`` no longer sets ``code="ValidationError"`` when an error
  with no code which appears to be validation related is parsed. Like other
  error classes, the default when no ``code`` is set is ``None``. (:pr:`NUMBER`)
