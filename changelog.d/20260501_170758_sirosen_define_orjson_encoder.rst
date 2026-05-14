Added
-----

-   The SDK now supports use of ``orjson`` as an alternative JSON encoder and decoder.
    When ``GLOBUS_SDK_USE_ORJSON=1`` is set, request sending and response decoding
    will use ``orjson``. (:pr:`NUMBER`)

    -   Use of ``orjson`` is optional, but if the variable is set and ``orjson``
        is not installed, errors will be emitted.

    -   The setting can also be configured on transport objects with the init
        option, ``use_orjson=True``.

    -   In a future major version of the SDK, use of ``orjson`` will default to
        true when it is available.

-   ``RequestsTransport`` objects are now visible via
    ``RequestsTransport.get_current_transport()``, a staticmethod, while the
    transport is sending a request or being used to handle a response. This
    method raises a ``LookupError`` if there is no currently active transport.
    (:pr:`NUMBER`)

Deprecated
----------

-   The ``RequestsTransport`` class supports configuration of request encoding
    via a class-variable mapping, ``encoders``. This limits the ability of the
    SDK to apply per-object customizations, as in the case of ``orjson``
    support. The class variable ``encoders`` is deprecated, and users should
    leverage the new ``encoder_map`` instance variable instead.
