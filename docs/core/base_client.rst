BaseClient
==========

All service clients support the low level interface, provided by the
``BaseClient``, from which all client types inherit.

A client object contains a ``transport``, an object responsible for sending
requests, encoding data, and handling potential retries. It also may include an
optional ``authorizer``, an object responsible for handling token
authentication for requests.


Closing Resources via Clients
-----------------------------

When used as context managers, clients automatically call their ``close()``
method on exit.

Closing a client closes the transport object attached to it if the transport was
created implicitly during init.
This means a transport passed in from the outside will not be closed, but one
which is never directly accessed by the user will be.

For most cases, users are recommended to use the context manager form, and to
allow clients to both create and close the transport:

.. code-block:: python

    from globus_sdk import SearchClient, UserApp

    with UserApp("sample-app", client_id="FILL_IN_HERE") as app:
        with SearchClient(app=app) as client:
            ...  # any usage

    # after the context manager, any transport is implicitly closed

However, transports are created explicitly, they are not automatically closed,
and the user becomes responsible for closing them.
For example, in the following usage, the user must close the transport:

.. code-block:: python

    from globus_sdk import SearchClient, UserApp
    from globus_sdk.transport import RequestsTransport

    my_transport = RequestsTransport(http_timeout=120.0)

    with UserApp("sample-app", client_id="FILL_IN_HERE") as app:
        with SearchClient(app=app, transport=my_transport) as client:
            ...  # any usage

    # at this stage, the transport will not be closed
    # it should be explicitly closed
    my_transport.close()


.. note::

    The SDK cannot tell whether or not an explicitly passed transport was bound
    to a name before it was passed. Therefore, in usage like the following,
    the transport will not automatically be closed:

    .. code-block:: python

        with SearchClient(app=app, transport=RequestsTransport()) as client:
            ...

    In order to close the transport in such a case, you must explicitly close it.
    Since transports are bound to ``client.transport``, the following usage would be a valid
    resolution:

    .. code-block:: python

        with SearchClient(app=app, transport=RequestsTransport()) as client:
            ...

        client.transport.close()


Reference
---------

BaseClient
^^^^^^^^^^

.. autoclass:: globus_sdk.BaseClient
   :members: scopes, resource_server, attach_globus_app, get, put, post, patch, delete, request
   :member-order: bysource
