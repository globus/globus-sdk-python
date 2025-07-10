.. _token_storages:

.. currentmodule:: globus_sdk.token_storage

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


Validating Token Storage
^^^^^^^^^^^^^^^^^^^^^^^^

Alongside the above storage-specific implementations which supply built-in token storage
to common locations, the SDK provides a unique token storage called
:class:`ValidatingTokenStorage`. This class isn't concerned with the actual storage of
tokens, but rather their validity.

A :class:`ValidatingTokenStorage` is created with one or more
:class:`TokenDataValidators <TokenDataValidator>`, each of which define a custom token
validation that will be performed during the storage or retrieval of a token. The SDK
provides a number of validators out-of-the-box to meet common validation requirements:
:ref:`token_data_validators`.


.. autoclass:: ValidatingTokenStorage

.. autoclass:: TokenDataValidator
    :members:
    :member-order: bysource

.. autoclass:: TokenValidationContext
    :members:
    :member-order: bysource

.. autoclass:: TokenValidationError
    :members:
    :member-order: bysource

.. _token_data_validators:
.. rubric:: Concrete Validators

.. autoclass:: NotExpiredValidator

.. autoclass:: HasRefreshTokensValidator

.. autoclass:: ScopeRequirementsValidator

.. autoclass:: UnchangingIdentityIDValidator
