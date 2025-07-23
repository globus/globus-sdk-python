Removed
-------

- Removed ``TransferClient`` methods for modifying "endpoint servers", a
  feature specific to Globus Connect Server v4. Specifically,
  ``add_endpoint_server``, ``update_endpoint_server``, and
  ``delete_endpoint_server``.
  These methods were deprecated in ``globus-sdk`` version 3. (:pr:`NUMBER`)
