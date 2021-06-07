BaseClient
==========

All service clients support the low level interface, provided by the
``BaseClient``, from which all client types inherit.

A client object contains a ``transport``, an object responsible for sending
requests, encoding data, and handling potential retries. It also may include an
optional ``authorizer``, an object responsible for handling token
authentication for requests.

BaseClient
----------

.. autoclass:: globus_sdk.client.BaseClient
   :members: retry_policy, get, put, post, patch, delete, request
   :member-order: bysource
