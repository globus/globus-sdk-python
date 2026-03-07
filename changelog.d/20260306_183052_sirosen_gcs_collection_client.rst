Added
-----

- Added a new ``GCSCollectionClient`` class in
  ``globus_sdk.experimental.gcs_collection_client``.
  The new client has no methods other than the base HTTP ones, but contains the
  collection ID and scopes in the correct locations for the SDK token management
  mechanisms to use. (:pr:`NUMBER`)
