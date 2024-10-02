.. _globus_app_config:

.. currentmodule:: globus_sdk.globus_app

GlobusApp Configuration
=======================

Reference
---------

Data Model
^^^^^^^^^^

.. autoclass:: globus_sdk.GlobusAppConfig()
    :members:
    :exclude-members: token_validation_error_handler
    :member-order: bysource

Providers
^^^^^^^^^

.. autoclass:: TokenStorageProvider()
    :members: for_globus_app
    :member-order: bysource

.. autoclass:: LoginFlowManagerProvider()
    :members: for_globus_app
    :member-order: bysource

.. autoclass:: TokenValidationErrorHandler()
    :members:
    :special-members: __call__
    :member-order: bysource
