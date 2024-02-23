Globus Connect Server API
=========================

.. currentmodule:: globus_sdk

The Globus Connect Server Manager API (GCS Manager API) runs on a
Globus Connect Server Endpoint and allows management of the Endpoint,
Storage Gateways, Collections, and other resources.

Unlike other Globus services, there is no single central API used to contact
GCS Manager instances. Therefore, the :class:`GCSClient` is always initialized with
the FQDN (DNS name) of the GCS Endpoint.
e.g. ``gcs = GCSClient("abc.def.data.globus.org")``

Client
------

The primary interface for the GCS Manager API is the :class:`GCSClient` class.

.. autoclass:: GCSClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

.. autoclass:: ConnectorTable
   :members:
   :show-inheritance:

.. autoclass:: GlobusConnectServerConnector
   :members:
   :show-inheritance:

.. automodule:: globus_sdk.services.gcs.data
   :members:
   :show-inheritance:

Client Errors
-------------

.. currentmodule:: globus_sdk

When an error occurs, a :class:`GCSClient` will raise this specialized type of
error, rather than a generic :class:`GlobusAPIError`.

.. autoclass:: GCSAPIError
   :members:
   :show-inheritance:

GCS Responses
-------------

.. automodule:: globus_sdk.services.gcs.response
   :members:
   :show-inheritance:
