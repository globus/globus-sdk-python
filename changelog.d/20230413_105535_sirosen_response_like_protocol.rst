* Make the request-like interface for response objects and errors more uniform. (:pr:`NUMBER`)

  * Both ``GlobusHTTPResponse`` and ``GlobusAPIError`` are updated to ensure
    that they have the following properties in common: ``http_status``,
    ``http_reason``, ``headers``, ``content_type``, ``text``

  * ``GlobusAPIError.raw_text`` is deprecated in favor of ``text``

  * ``GlobusHTTPResponse`` and ``GlobusAPIError`` have both gained a new
    property, ``binary_content``, which returns the unencoded response data as
    bytes
