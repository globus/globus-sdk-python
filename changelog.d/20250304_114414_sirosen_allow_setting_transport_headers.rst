Added
~~~~~

- The ``transport`` attached to clients now exposes ``headers`` as a readable
  and writable dict of headers which will be included in every request.
  Headers provided to the transport's ``request()`` method overwrite these, as
  before. (:pr:`NUMBER`)

Changed
~~~~~~~

- Updates to ``X-Globus-Client-Info`` in ``RequestsTransport.headers`` are now
  synchronized via a callback mechanism. Direct manipulations of the ``infos``
  list will not result in headers being updated -- callers wishing to modify
  these data should rely only on the ``add()`` and ``clear()`` methods of the
  ``GlobusClientInfo`` object. (:pr:`NUMBER`)
