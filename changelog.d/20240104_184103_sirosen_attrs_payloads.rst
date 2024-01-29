Changed
~~~~~~~

- ``globus-sdk`` now depends on the ``attrs`` library. (:pr:`NUMBER`)

Development
~~~~~~~~~~~

- A new component has been added for definition of payload classes, at
  ``globus_sdk.payload``, based on ``attrs``. (:pr:`NUMBER`)

  - New payload classes should inherit from ``globus_sdk.payload.Payload``

  - ``attrs``-style converter definitions are defined at
    ``globus_sdk.payload.converters``

  - ``Payload`` objects are fully supported by transport encoding, in a similar
    way to ``utils.PayloadWrapper`` objects.

  - ``Payload``\s always support a field named ``extra`` which can be used to
    incorporate additional data into the payload body, beyond the supported
    fields.

  - ``Payload`` objects require that all of their arguments are keyword-only

  - ``Payload.extra`` assignment emits a ``RuntimeWarning`` if field names
    collide with existing fields. This is the strongest signal we can give to
    users that they should not do this short of emitting an error. Erroring is
    not an option because it would make every field addition a breaking change.
