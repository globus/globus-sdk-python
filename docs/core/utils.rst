Utilities
=========

.. warning::

    These components are *not* intended for outside use, but are internal to
    the Globus SDK.

    They may change in backwards-incompatible ways in minor or patch releases
    of the SDK.

    This documentation is included here for completeness.


MissingType and MISSING
-----------------------

The ``MISSING`` sentinel value is used as an alternative to ``None`` in APIs
which accept ``null`` as a valid value. Whenever ``MISSING`` is included in a
request, it will be removed before the request is sent to the service.

As a result, where ``MISSING`` is used as the default for a value, ``None`` can
be used to explicitly pass the value ``null``.

.. class:: globus_sdk.MissingType
    :canonical: globus_sdk._missing.MissingType

    This is the type of ``MISSING``.

.. py:data:: globus_sdk.MISSING

    The ``MISSING`` sentinel value. It is a singleton.
