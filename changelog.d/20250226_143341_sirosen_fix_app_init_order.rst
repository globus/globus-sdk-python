Changed
~~~~~~~

- The initialization of a client with a ``GlobusApp`` has been improved and is
  now available under the public ``attach_globus_app`` method on client
  classes. Attaching an app is only valid for clients which were initialized
  without an app or authorizer. (:pr:`NUMBER`)
