.. _token_storages:

.. currentmodule:: globus_sdk.tokenstorage

Token Storages
==============

Interacting with Globus services requires the use of Globus Auth-issued OAuth2 tokens.
To assist in reuse of these tokens, the SDK provides an interface to store and
retrieve this data across different storage backends.

In addition to the interface, :class:`TokenStorage`, the SDK provides concrete
implementations for some of the most common storage backends:

-   :class:`JSONTokenStorage` for storing tokens in a local JSON file.
-   :class:`SQLiteTokenStorage` for storing tokens in a local SQLite database.
-   :class:`MemoryTokenStorage` for storing tokens in process memory.


Reference
---------

.. autoclass:: TokenStorage
    :members:
    :member-order: bysource


.. autoclass:: TokenStorageData
    :members:
    :member-order: bysource


File-based Token Storages
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: JSONTokenStorage

.. autoclass:: SQLiteTokenStorage
    :members: close, iter_namespaces


Ephemeral Token Storages
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: MemoryTokenStorage

