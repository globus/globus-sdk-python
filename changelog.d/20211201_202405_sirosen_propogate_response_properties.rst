* The implementation of several properties of ``GlobusHTTPResponse`` has
  changed (:pr:`NUMBER`)

  * Responses have a new property, ``headers``, a case-insensitive
    dict of headers from the response

  * Responses now implement ``http_status`` and ``content_type`` as
    properties without setters
