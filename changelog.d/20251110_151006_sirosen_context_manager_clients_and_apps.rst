Fixed
-----

- Fixed a resource leak in which a ``GlobusApp`` would create internal client
  objects and never close the associated transports. (:pr:`NUMBER`)
