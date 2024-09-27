
Token Caching
=============

The documentation in this section provides references for interfaces and standard
implementations for caching OAuth2 tokens. While there are two distinct class
hierarchies, :ref:`token_storages` and its predecessor :ref:`storage_adapters`, we
recommend using the former. ``TokenStorage`` is a newer iteration of the token storage
interface and includes a superset of the functionality previously supported in
``StorageAdapter``.

All constructs from both hierarchies are importable from the ``globus_sdk.tokenstorage``
namespace.

.. toctree::
    :maxdepth: 1

    token_storages
    storage_adapters

