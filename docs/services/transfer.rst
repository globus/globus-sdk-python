Globus Transfer
===============

Client
------

The primary interface for the Globus Transfer API is the ``TransferClient``
class.

.. autoclass:: globus_sdk.TransferClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

These helper objects make it easier to correctly create data for consumption by
a ``TransferClient``.

.. autoclass:: globus_sdk.TransferData
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.DeleteData
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a ``TransferClient`` will raise this specialized type of
error, rather than a generic ``GlobusAPIError``.

.. autoclass:: globus_sdk.TransferAPIError
   :members:
   :show-inheritance:

Transfer Responses
------------------

.. automodule:: globus_sdk.services.transfer.response
   :members:
   :show-inheritance:
