Changed
~~~~~~~

- Payload types now inherit from ``dict`` rather than ``UserDict``. The
  ``PayloadWrapper`` utility class has been replaced with ``Payload``.
  (:pr:`1222`)
- Payload types are more consistent about encoding missing values using ``MISSING``.
  (:pr:`1222`)
