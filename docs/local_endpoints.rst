.. _local_endpoints:

Local Endpoints
===============

.. currentmodule:: globus_sdk

Unlike SDK functionality for accessing Globus APIs, the locally available
Globus Endpoints require special treatment.
These accesses are not authenticated via Globus Auth, and may rely upon the
state of the local filesystem, running processes, and the permissions of local
users.

Globus Connect Server
---------------------

.. autoclass:: LocalGlobusConnectServer
   :members:
   :member-order: bysource

Globus Connect Personal
-----------------------

Globus Connect Personal endpoints belonging to the current user may be accessed
via instances of the following class:

.. autoclass:: LocalGlobusConnectPersonal
   :members:
   :member-order: bysource

.. autoclass:: GlobusConnectPersonalOwnerInfo
   :members:
   :member-order: bysource
