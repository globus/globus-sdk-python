Added
~~~~~

- The ``jwt_params`` argument to ``decode_id_token()`` now allows ``"leeway"``
  to be included to pass a ``leeway`` parameter to pyjwt. (:pr:`NUMBER`)

Fixed
~~~~~

- ``decode_id_token()`` defaulted to having no tolerance for clock drift. Slight
  clock drift could lead to JWT claim validation errors. The new default is
  0.5s which should be sufficient for most cases. (:pr:`NUMBER`)
