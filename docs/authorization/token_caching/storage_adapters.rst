.. _storage_adapters:

Storage Adapters (Legacy)
=========================

.. warning::

    The class hierarchy documented here is legacy.

    We recommend using the newer class hierarchy documented at :ref:`token_storages`.

The StorageAdapter component provides a way of storing and loading the tokens
received from authentication and token refreshes.

Usage
-----

StorageAdapter is available under the name ``globus_sdk.token_storage``.

Storage adapters are the main objects of this subpackage. Primarily, usage
should revolve around creating a storage adapter, potentially loading data from
it, and using it as the ``on_refresh`` handler for an authorizer.

For example:

.. code-block:: python

    import os
    import globus_sdk
    from globus_sdk.token_storage import SimpleJSONFileAdapter

    my_file_adapter = SimpleJSONFileAdapter(os.path.expanduser("~/mytokens.json"))

    if not my_file_adapter.file_exists():
        # ... do a login flow, getting back initial tokens
        # elided for simplicity here
        token_response = ...
        # now store the tokens, and pull out the tokens for the
        # resource server we want
        my_file_adapter.store(token_response)
        by_rs = token_response.by_resource_server
        tokens = by_rs["transfer.api.globus.org"]
    else:
        # otherwise, we already did this whole song-and-dance, so just
        # load the tokens from that file
        tokens = my_file_adapter.get_token_data("transfer.api.globus.org")


    # RereshTokenAuthorizer and ClientCredentialsAuthorizer both use
    # `on_refresh` callbacks
    # this feature is therefore only relevant for those auth types
    #
    # auth_client is the internal auth client used for refreshes,
    # and which was used in the login flow
    # note that this is all normal authorizer usage wherein
    # my_file_adapter is providing the on_refresh callback
    auth_client = ...
    authorizer = globus_sdk.RefreshTokenAuthorizer(
        tokens["refresh_token"],
        auth_client,
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=my_file_adapter.on_refresh,
    )

    # or, for client credentials
    authorizer = globus_sdk.ClientCredentialsAuthorizer(
        auth_client,
        ["urn:globus:auth:transfer.api.globus.org:all"],
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=my_file_adapter.on_refresh,
    )

    # and then use the authorizer on a client!
    tc = globus_sdk.TransferClient(authorizer=authorizer)


Complete Example Usage
~~~~~~~~~~~~~~~~~~~~~~

The :ref:`Group Listing With Token Storage Script <example_group_listing_with_token_storage>`
provides a complete and runnable example which leverages ``token_storage``.


Adapter Types
-------------

.. module:: globus_sdk.token_storage

``globus_sdk.token_storage`` provides base classes for building your own storage
adapters, and several complete adapters.

The :class:`SimpleJSONFileAdapter` is good for the "simplest possible"
persistent storage, using a JSON file to store token data.

:class:`MemoryAdapter` is even simpler still, and is great for writing and
testing code which uses the ``StorageAdapter`` interface backed by an in-memory
structure.

The :class:`SQLiteAdapter` is more complex, for applications like the
globus-cli which need to store various tokens and additional configuration. In
addition to basic token storage, the :class:`SQLiteAdapter` provides for namespacing
of the token data, and for additional configuration storage.

Reference
---------

.. autoclass:: StorageAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: MemoryAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: FileAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: SimpleJSONFileAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: SQLiteAdapter
   :members:
   :member-order: bysource
   :show-inheritance:
