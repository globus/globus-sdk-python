Added
~~~~~

- ``AuthClient.oauth2_get_authorize_url`` now supports the following parameters
  for session management: ``session_required_identities``,
  ``session_required_single_domain``, and ``session_required_policies``. Each
  of these accept list inputs, as returned by
  ``ErrorInfo.authorization_parameters``. (:pr:`NUMBER`)
