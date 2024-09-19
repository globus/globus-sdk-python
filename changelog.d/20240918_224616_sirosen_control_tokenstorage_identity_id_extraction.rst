Fixed
~~~~~

.. rubric:: Experimental

- Fix the handling of Dependent Token and Refresh Token responses in
  ``TokenStorage`` and ``GlobusApp``'s internal ``ValidatingTokenStorage`` in
  order to ensure that ``id_token`` is only parsed when appropriate. (:pr:`NUMBER`)
