Removed
-------

- Removed support for Endpoint Activation, a feature which was specific to
  Globus Connect Server v4. (:pr:`NUMBER`)

  - Removed the activation methods: ``TransferClient.endpoint_autoactivate``,
    ``TransferClient.endpoint_activate``,
    ``TransferClient.endpoint_deactivate``, and
    ``TransferClient.endpoint_get_activation_requirements``

  - Removed the specialized ``ActivationRequirementsResponse`` parsed response
    type

  - ``TransferClient.update_endpoint`` would previously check the
    ``myproxy_server`` and ``oauth_server`` parameters, which were solely used
    for the purpose of configuring activation. It no longer does so.
