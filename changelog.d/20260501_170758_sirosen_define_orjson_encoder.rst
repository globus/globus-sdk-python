Added
-----

-   The SDK now supports use of ``orjson`` as an alternative JSON encoder and decoder.
    When ``orjson`` is installed, the SDK will automatically use it in place of
    the stdlib ``json`` module. (:pr:`1385`)

-   ``RequestsTransport`` objects are now visible via
    ``RequestsTransport.get_current_transport()``, a staticmethod, while the
    transport is sending a request or being used to handle a response. This
    method raises a ``LookupError`` if there is no currently active transport.
    (:pr:`1385`)

-   The request encoders defined in ``globus_sdk.transport`` have been
    refactored into ``RequestsRepresentationProvider``\s, objects responsible
    for encoding and decoding ``requests`` data in specific formats. In order to
    retain compatibility, they are still available aliased under their previous
    names, as "encoders".

Deprecated
----------

-   The ``RequestsTransport`` class supports configuration of request encoding
    via a class-variable mapping, ``encoders``. This limits the ability of the
    SDK to apply per-object customizations, as in the case of ``orjson``
    support. The class variable ``encoders`` is deprecated. Users who wish to
    customize request encoding and response decoding should leverage the new
    ``representation_providers`` instance variable instead.

-   The ``globus_sdk.transport.encoders`` module is deprecated. Use
    ``globus_sdk.transport.representation_providers`` instead.
