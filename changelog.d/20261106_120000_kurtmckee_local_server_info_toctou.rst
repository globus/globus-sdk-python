Fixed
-----

- ``LocalGlobusConnectServer.info_dict`` can no longer raise ``FileNotFoundError``
  if the ``info.json`` file is removed while it is being loaded. (:pr:`1444`)
