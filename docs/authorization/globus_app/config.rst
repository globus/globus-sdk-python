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

..
    In the above class, "token_validation_error_handler" is a callable so sphinx wants
    to document it as a method. Instead, we explicitly exclude it and document it in the
    class docstring as an `ivar`.

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
