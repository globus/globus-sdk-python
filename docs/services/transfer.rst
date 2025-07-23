Globus Transfer
===============

.. currentmodule:: globus_sdk

Client
------

The primary interface for the Globus Transfer API is the :class:`TransferClient`
class.

.. autoclass:: TransferClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

These helper objects make it easier to correctly create data for consumption by
a :class:`TransferClient`.

.. autoclass:: TransferData
   :members:
   :show-inheritance:

.. autoclass:: DeleteData
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`TransferClient` will raise this specialized type of
error, rather than a generic :class:`GlobusAPIError`.

.. autoclass:: TransferAPIError
   :members:
   :show-inheritance:

Transfer Responses
------------------

.. autoclass:: IterableTransferResponse
   :members:
   :show-inheritance:
