.. module:: globus_sdk.search


Globus Search
=============

.. autoclass:: globus_sdk.SearchClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

.. autoclass:: globus_sdk.SearchQuery
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a ``SearchClient`` will raise this specialized type of
error, rather than a generic ``GlobusAPIError``.

.. autoclass:: globus_sdk.SearchAPIError
   :members:
   :show-inheritance:
