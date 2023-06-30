Added
~~~~~

- ``globus_sdk._testing`` now exposes a method, ``construct_error`` which makes
  it simpler to explicitly construct and return a Globus SDK error object for
  testing. This is used in the SDK's own testsuite and is available for
  ``_testing`` users. (:pr:`NUMBER`)
