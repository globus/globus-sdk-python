Changed
~~~~~~~

* ``AuthClient``, ``NativeAppAuthClient``, and ``ConfidentialAppAuthClient``
  have had their init signatures updated to explicitly list available
  parameters. (:pr:`764`)

  * Type annotations for these classes are now more accurate

  * The ``NativeAppAuthClient`` and ``ConfidentialAppAuthClient`` classes do
    not accept ``authorizer`` in their init signatures. Previously this was
    accepted but raised a ``GlobusSDKUsageError``. Attempting to pass an
    ``authorizer`` will now result in a ``TypeError``.
