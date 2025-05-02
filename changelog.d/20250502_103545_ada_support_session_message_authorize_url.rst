Added
~~~~~

- ``AuthLoginClient`` now supports a ``session_message`` when constructing an
  OAuth2 authorization URL. (:pr:`NUMBER`)
- ``LoginFlowManager`` will now use a ``session_message`` present in the
  supplied ``GlobusAuthorizationParameters`` as part of the login flow. (:pr:`NUMBER`)
