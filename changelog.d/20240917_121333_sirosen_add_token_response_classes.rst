Changed
~~~~~~~

- The response types for different OAuth2 token grants now vary by the grant
  type. For example, a ``refresh_token`` grant will now produce a
  ``RefreshTokenResponse``. This allows code handling responses to identify
  which grant type was used to produce a response. (:pr:`NUMBER`)

  - The following new types have been introduced:
    ``globus_sdk.RefreshTokenResponse``,
    ``globus_sdk.AuthorizationCodeTokenResponse``,
    ``globus_sdk.ClientCredentialsTokenResponse``.

  - The ``RenewingAuthorizer`` class is now a generic over the response type
    which it handles, and the subtypes of authorizers are specialized for their
    types of responses. e.g.,
    ``class RefreshTokenAuthorizer(RenewingAuthorizer[RefreshTokenResponse])``.
