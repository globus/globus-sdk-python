Fixed
-----

- Fixed a bug in ``globus_sdk.TransferData`` which failed to convert
  ``deadline`` to a string when a ``datetime.datetime`` object is given.
  (:pr:`1372`)
