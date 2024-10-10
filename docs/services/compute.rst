Globus Compute
==============

.. currentmodule:: globus_sdk

..  autoclass:: ComputeClient
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.ComputeScopes
            :base_name: ComputeClient.scopes

Helper Objects
--------------

.. autoclass:: ComputeFunctionDocument
   :members:
   :show-inheritance:

.. autoclass:: ComputeFunctionMetadata
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`ComputeClient` will raise a ``ComputeAPIError``.

.. autoclass:: ComputeAPIError
   :members:
   :show-inheritance:
