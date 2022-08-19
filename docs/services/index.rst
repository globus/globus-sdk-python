.. _services:

Service Clients
===============

.. currentmodule:: globus_sdk

The Globus SDK provides a client class for every public Globus API.
Each client object takes authentication credentials from config files,
environment variables, or programmatically via :ref:`GlobusAuthorizers <authorization>`.

Once instantiated, a Client gives you high-level interface to make API calls,
without needing to know Globus API endpoints or their various parameters.

For example, you could use the :class:`TransferClient` to list your task history
very simply::

    from globus_sdk import TransferClient, AccessTokenAuthorizer

    # you must have a valid transfer token for this to work
    tc = TransferClient(
        authorizer=AccessTokenAuthorizer("TRANSFER_TOKEN_STRING")
    )

    print("My Last 25 Tasks:")
    # `filter` to get Delete Tasks (default is just Transfer Tasks)
    for task in tc.task_list(num_results=25, filter="type:TRANSFER,DELETE"):
        print(task["task_id"], task["type"], task["status"])

.. note:: Multi-Thread and Multi-Process Safety

    Each Globus SDK client class holds a networking session object to interact
    with the Globus API. Using a previously created service client object after
    forking or between multiple threads should be considered unsafe. In
    multi-processing applications, it is recommended to create service client
    objects after process forking and to ensure that there is only one service
    client instance created per process.

.. toctree::
    :caption: Service Clients
    :maxdepth: 1

    auth
    flows
    groups
    search
    timer
    transfer
    gcs
