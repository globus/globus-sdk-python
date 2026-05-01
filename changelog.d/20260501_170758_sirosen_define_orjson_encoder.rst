Added
-----

-   The SDK now supports use of ``orjson`` as an alternative JSON encoder and decoder.
    When ``GLOBUS_SDK_PREFER_ORJSON=1`` is set, request sending and response decoding
    will prefer to use ``orjson`` if it is installed and available, gracefully failing
    over to the standard library ``json`` module if it is not. This setting will become
    the default behavior in a future major version of the SDK. (:pr:`NUMBER`)
