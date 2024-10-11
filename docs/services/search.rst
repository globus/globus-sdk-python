Globus Search
=============

.. currentmodule:: globus_sdk

.. autoclass:: SearchClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

Note that you should not use
:class:`SearchQueryBase <globus_sdk.services.search.data.SearchQueryBase>` directly,
and it is not importable from the top level of the SDK. It is included in documentation
only to document the methods it provides to its subclasses.

.. autoclass:: globus_sdk.services.search.data.SearchQueryBase
   :members:
   :show-inheritance:

.. autoclass:: SearchQuery
   :members:
   :show-inheritance:

.. autoclass:: SearchQueryV1
    :members:
    :show-inheritance:

.. autoclass:: SearchScrollQuery
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`SearchClient` will raise this specialized type of
error, rather than a generic :class:`GlobusAPIError`.

.. autoclass:: SearchAPIError
   :members:
   :show-inheritance:
