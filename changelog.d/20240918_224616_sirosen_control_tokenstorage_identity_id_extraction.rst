Fixed
~~~~~

- Fix the handling of Dependent Token and Refresh Token responses in
  ``TokenStorage`` and ``ValidatingTokenStorage`` in order to ensure
  that ``id_token`` is only parsed when appropriate. (:pr:`1055`)
