Breaking Changes
----------------

- Removed support for ``ConfidentialAppAuthClient.get_identities``.
  This usage was deprecated in ``globus-sdk`` version 3. (:pr:`NUMBER`)

  - Users calling the Get Identities API on behalf of a client identity should
    instead get tokens for the client and use those tokens to call
    ``AuthClient.get_identities``. For example, by instantiating an
    ``AuthClient`` using a ``ClientCredentialsAuthorizer``.

  - This also means that it is no longer valid to use a
    ``ConfidentialAppAuthClient`` to initialize an ``IdentityMap``.
