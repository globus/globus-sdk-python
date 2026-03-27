Added
-----

- Added the experimental ``TransferClientV2`` client class along with helper
  classes ``TunnelCreateDocument`` and ``TunnelUpdateDocument`` (:pr:`NUMBER`)
- JSON:API iteration and pagination is now supported through
  ``IterableJSONAPIResponse`` and ``JSONAPIPaginator`` (:pr:`NUMBER`)

Changed
-------

- All tunnels support in ``TransferClient`` has been labeled as Beta as the
  underlying API is still in development. For the most up to date interfaces
  it is recommended to use the ``TransferClientV2`` (:pr:`NUMBER`)

Fixed
-----

- Various fixes for tunnels support in ``TransferClient`` (:pr:`NUMBER`)
