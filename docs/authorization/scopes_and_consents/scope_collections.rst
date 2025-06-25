.. _scope_collections:

.. currentmodule:: globus_sdk.scopes

ScopeCollections
================

OAuth2 Scopes for various Globus services are represented by ``ScopeCollection``
objects.
These are containers for constant :class:`Scope` objects.

Scope collections are provided directly via ``globus_sdk.scopes`` and are also
accessible via the relevant client classes.

Direct Use
----------

To use the scope collections directly, import from ``globus_sdk.scopes``.

For example, one might use the Transfer "all" scope during a login flow like
so:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[TransferScopes.all])
    ...

As Client Attributes
--------------------

Token scopes are associated with a particular client which will use that token.
Because of this, each service client contains a ``ScopeCollection`` attribute
(``client.scopes``) defining the relevant scopes for that client.

For most client classes, this is a class attribute. For example, accessing
``TransferClient.scopes`` is valid:

.. code-block:: python

    import globus_sdk

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[globus_sdk.TransferClient.scopes.all])
    ...

    # or, potentially, after there is a concrete client
    tc = globus_sdk.TransferClient()
    client.oauth2_start_flow(requested_scopes=[tc.scopes.all])

As Instance Attributes and Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some client classes only provide their scopes for instances. These cases cover
services which are distributed or contain multiple subservices with their own
scopes.

For example, ``GCSClient`` and ``SpecificFlowClient`` each have a ``scopes``
attribute of ``None`` on their classes.

In the case of ``SpecificFlowClient``, scopes are populated whenever an
instance is instantiated. So the following usage is valid:

.. code-block:: python

    import globus_sdk

    FLOW_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.SpecificFlowClient(FLOW_ID)
    flow_user_scope = client.scopes.user

In the case of GCS, a distributed service, ``scopes`` is always ``None``.
However, :meth:`globus_sdk.GCSClient.get_gcs_endpoint_scopes` and
:meth:`globus_sdk.GCSClient.get_gcs_collection_scopes` are available helpers
for getting specific collections of scopes.

Using a Scope Collection to Get Matching Tokens
-----------------------------------------------

A ``ScopeCollection`` contains the resource server name used to get token data
from a token response.
To elaborate on the above example:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[TransferScopes.all])
    authorize_url = client.oauth2_get_authorize_url()
    print("Please go to this URL and login:", authorize_url)
    auth_code = input("Please enter the code you get after login here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # use the `resource_server` of a ScopeBuilder to grab the associated token
    # data from the response
    tokendata = token_response.by_resource_server[TransferScopes.resource_server]


Reference
---------

Collection Types
~~~~~~~~~~~~~~~~

.. autoclass:: ScopeCollection
    :members:
    :show-inheritance:

.. autoclass:: StaticScopeCollection
    :members:
    :show-inheritance:

.. autoclass:: DynamicScopeCollection
    :members:
    :show-inheritance:

.. autoclass:: GCSEndpointScopes
    :members:
    :show-inheritance:

.. autoclass:: GCSCollectionScopes
    :members:
    :show-inheritance:

.. autoclass:: SpecificFlowScopes
    :members:
    :show-inheritance:

Collection Constants
~~~~~~~~~~~~~~~~~~~~

.. py:data:: globus_sdk.scopes.data.AuthScopes

    Globus Auth scopes.

    .. listknownscopes:: globus_sdk.scopes.AuthScopes
        :example_scope: view_identity_set


.. py:data:: globus_sdk.scopes.data.ComputeScopes

    Compute scopes.

    .. listknownscopes:: globus_sdk.scopes.ComputeScopes


.. py:data:: globus_sdk.scopes.data.FlowsScopes

    Globus Flows scopes.

    .. listknownscopes:: globus_sdk.scopes.FlowsScopes


.. py:data:: globus_sdk.scopes.data.GroupsScopes

    Groups scopes.

    .. listknownscopes:: globus_sdk.scopes.GroupsScopes


.. py:data:: globus_sdk.scopes.data.NexusScopes

    Nexus scopes.

    .. listknownscopes:: globus_sdk.scopes.NexusScopes

    .. warning::

        Use of Nexus is deprecated. Users should use Groups instead.


.. py:data:: globus_sdk.scopes.data.SearchScopes

    Globus Search scopes.

    .. listknownscopes:: globus_sdk.scopes.SearchScopes


.. py:data:: globus_sdk.scopes.data.TimersScopes

    Globus Timers scopes.

    .. listknownscopes:: globus_sdk.scopes.TimersScopes


.. py:data:: globus_sdk.scopes.data.TransferScopes

    Globus Transfer scopes.

    .. listknownscopes:: globus_sdk.scopes.TransferScopes
