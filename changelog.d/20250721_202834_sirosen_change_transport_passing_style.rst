Breaking Changes
----------------

- The ``RequestsTransport`` object has been refactored to separate it from
  configuration which controls request retries. A new ``RetryConfig`` object is
  introduced and provided as ``client.retry_config`` on all client types. The
  interface for controlling these configurations has been updated.
  (:pr:`NUMBER`)

  - The ``transport_class`` attribute has been removed from client classes.

  - Clients now accept ``transport``, an instance of ``RequestsTransport``, and
    ``retry_config``, an instance of ``RetryConfig``, instead of
    ``transport_params``.

  - Users seeking to customize the retry backoff, sleep maximum, and max
    retries should now use ``retry_config``, as these are no longer controlled
    through ``transport``.

  - The capabilities of the ``RequestsTransport.tune()`` context manager have
    been divided into ``RequestsTransport.tune()`` and ``RetryConfig.tune()``.

  - The retry configuration is exposed to retry checks as an attribute of the
    ``RequestCallerInfo``, which is provided on the ``RetryContext``. As a
    result, checks can examine the configuration.
