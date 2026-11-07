Fixed
-----

- ``RequestsTransport.tune()`` and ``RetryConfig.tune()`` now restore the settings
  even if an exception is raised. (:pr:`1448`)

  Previously, an exception inside a tuned context
  (like ``with client.transport.tune(verify_ssl=False):``)
  would leave the modified settings configured for subsequent requests.
