Exceptions
==========

All Globus SDK errors inherit from ``GlobusError``, and all SDK error classes
are importable from ``globus_sdk``.

You can therefore capture *all* errors thrown by the SDK by looking for
``GlobusError``, as in

.. code-block:: python

    import logging
    from globus_sdk import TransferClient, GlobusError

    try:
        tc = TransferClient(...)
        # search with no parameters will throw an exception
        eps = tc.endpoint_search()
    except GlobusError:
        logging.exception("Globus Error!")
        raise

In most cases, it's best to look for specific subclasses of ``GlobusError``.
For example, to write code which is distinguishes between network failures and
unexpected API conditions, you'll want to look for ``NetworkError`` and
``GlobusAPIError``

.. code-block:: python

    import logging
    from globus_sdk import TransferClient, GlobusError, GlobusAPIError, NetworkError

    try:
        tc = TransferClient(...)

        eps = tc.endpoint_search(filter_fulltext="myendpointsearch")

        for ep in eps:
            print(ep["display_name"])

        ...
    except GlobusAPIError as e:
        # Error response from the REST service, check the code and message for
        # details.
        logging.error(
            "Got a Globus API Error\n"
            f"Error Code: {e.code}\n"
            f"Error Message: {e.message}"
        )
        raise e
    except NetworkError:
        logging.error("Network Failure. Possibly a firewall or connectivity issue")
        raise
    except GlobusError:
        logging.exception("Totally unexpected GlobusError!")
        raise
    else:
        ...

Of course, if you want to learn more information about the response, you should
inspect it more than this.

All errors raised by the SDK should be instances of ``GlobusError``.
Malformed calls to Globus SDK methods typically raise ``GlobusSDKUsageError``,
but, in rare cases, may raise standard python exceptions (``ValueError``,
``OSError``, etc.)


Error Classes
-------------

.. autoclass:: globus_sdk.GlobusError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.GlobusSDKUsageError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.GlobusAPIError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.NetworkError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.GlobusConnectionError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.GlobusTimeoutError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.GlobusConnectionTimeoutError
   :members:
   :show-inheritance:

ErrorInfo
---------

``GlobusAPIError`` and its subclasses all support an ``info`` property which
may contain parsed error data. The ``info`` is guaranteed to be there, but its
attributes should be tested before use, as in

.. code-block:: python

    # if 'err' is an API error, then 'err.info' is an 'ErrorInfoContainer',
    # a wrapper which holds ErrorInfo objects
    # 'err.info.consent_required' is a 'ConsentRequiredInfo', which should be
    # tested for truthy/falsey-ness before use
    if err.info.consent_required:
        print(
            "Got a ConsentRequired error with scopes:",
            err.info.consent_required.required_scopes,
        )

.. autoclass:: globus_sdk.exc.ErrorInfoContainer
    :members:

.. autoclass:: globus_sdk.exc.ErrorInfo
    :members:

.. autoclass:: globus_sdk.exc.AuthorizationParameterInfo
    :members:
    :show-inheritance:

.. autoclass:: globus_sdk.exc.ConsentRequiredInfo
    :members:
    :show-inheritance:
