* When users input empty ``requested_scopes`` values, these are now rejected
  with a usage error instead of being translated into the default set of
  ``requested_scopes`` (:pr:`NUMBER`)

* Users may now opt-in to deprecation warnings about features which are planned
  to change in version 4.0.0 of the ``globus-sdk``. Setting the environment
  variable ``GLOBUS_SDK_V4_WARNINGS=true`` will enable these warnings. One
  such warning is emitted when ``requested_scopes`` is omitted or specified as
  ``None``. In v4 of ``globus-sdk``, users will always be required to specify
  their scopes when doing login flows. (:pr:`NUMBER`)
