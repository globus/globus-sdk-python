Added
-----

- Added the experimental ``TransferClientV2`` client class along with helper
  classes ``TunnelCreateDocument`` and ``TunnelUpdateDocument`` (:pr:`1370`)
- JSON:API iteration and pagination is now supported through
  ``IterableJSONAPIResponse`` and ``JSONAPIPaginator`` (:pr:`1370`)

Changed
-------

- All tunnels support in ``TransferClient`` has been labeled as Beta as the
  underlying API is still in development. For the most up to date interfaces
  it is recommended to use the ``TransferClientV2`` (:pr:`1370`)

Fixed
-----

- Various fixes for tunnels support in ``TransferClient`` (:pr:`1370`)
