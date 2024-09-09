.. _scopes:

.. currentmodule:: globus_sdk.scopes

Scopes and ScopeBuilders
========================

OAuth2 Scopes for various Globus services are represented by ``ScopeBuilder``
objects.

A number of pre-set scope builders are provided and populated with useful data,
and they are also accessible via the relevant client classes.

Direct Use (as constants)
-------------------------

To use the scope builders directly, import from ``globus_sdk.scopes``.

For example, one might use the Transfer "all" scope during a login flow like
so:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[TransferScopes.all])
    ...

As Client Class Attributes
--------------------------

Token scopes are associated with a particular client, the one which will use that token. Because of this, each service client contains a ``ScopeBuilder`` attribute (``client.scopes``) defining the relevant scopes for that client.

.. code-block:: python

    import globus_sdk

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[globus_sdk.TransferClient.scopes.all])
    ...

    # or, potentially, after there is a concrete client
    _tc = globus_sdk.TransferClient()
    client.oauth2_start_flow(requested_scopes=[_tc.scopes.all])

Using a Scope Builder to Get Matching Tokens
--------------------------------------------

A ``ScopeBuilder`` contains the resource server name used to get token data
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

Scope objects
-------------

In order to support optional and dependent scopes, an additional type is
provided by ``globus_sdk.scopes``: the ``Scope`` class.

``Scope`` can be constructed using its initializer, or one of its two main
parsing methods: ``Scope.parse`` and ``Scope.deserialize``.
``parse`` produces a list of scopes from a string, while ``deserialize``
produces exactly one.

For example, one can create a ``Scope`` from the Groups "all" scope
as follows:

.. code-block:: python

    from globus_sdk.scopes import GroupsScopes, Scope

    group_scope = Scope.deserialize(GroupsScopes.all)

``Scope`` objects primarily provide three main pieces of functionality:

    * parsing (deserializing)
    * stringifying (serializing)
    * dynamic scope tree building

Dynamic Scope Construction
~~~~~~~~~~~~~~~~~~~~~~~~~~

``Scope`` objects provide a tree-like interface for constructing scopes
and their dependencies.

For example, the transfer scope dependent upon a collection scope may be
constructed by means of ``Scope`` methods thusly:

.. code-block:: python

    from globus_sdk.scopes import GCSCollectionScopeBuilder, TransferScopes, Scope

    MAPPED_COLLECTION_ID = "...ID HERE..."

    # create the scope object, and get the data_access_scope as a string
    transfer_scope = Scope(TransferScopes.all)
    data_access_scope = GCSCollectionScopeBuilder(MAPPED_COLLECTION_ID).data_access
    # add data_access as an optional dependency
    transfer_scope.add_dependency(data_access_scope, optional=True)

``Scope``\s can be used in most of the same locations where scope
strings can be used, but you can also call ``scope.serialize()`` to get a
stringified representation.

Serializing Scopes
~~~~~~~~~~~~~~~~~~

Whenever scopes are being sent to Globus services, they need to be encoded as
strings. All scope objects support this by means of their defined
``serialize`` method. Note that ``__str__`` for a ``Scope`` is just an
alias for ``serialize``. For example, the following is valid usage to demonstrate
``str()``, ``repr()``, and ``serialize()``:

.. code-block:: pycon

    >>> from globus_sdk.scopes import Scope
    >>> foo = Scope("foo")
    >>> bar = Scope("bar")
    >>> bar.add_dependency("baz")
    >>> foo.add_dependency(bar)
    >>> print(str(foo))
    foo[bar[baz]]
    >>> print(bar.serialize())
    bar[baz]
    >>> alpha = Scope("alpha")
    >>> alpha.add_dependency("beta", optional=True)
    >>> print(str(alpha))
    alpha[*beta]
    >>> print(repr(alpha))
    Scope("alpha", dependencies=[Scope("beta", optional=True)])

Scope Reference
~~~~~~~~~~~~~~~

.. autoclass:: Scope
   :members:
   :member-order: bysource

.. autoclass:: ScopeParseError

.. autoclass:: ScopeCycleError

ScopeBuilders
-------------

ScopeBuilder Types
~~~~~~~~~~~~~~~~~~

.. autoclass:: ScopeBuilder
    :members:
    :show-inheritance:

.. autoclass:: GCSEndpointScopeBuilder
    :members:
    :show-inheritance:

.. autoclass:: GCSCollectionScopeBuilder
    :members:
    :show-inheritance:

.. autoclass:: SpecificFlowScopeBuilder
    :members:
    :show-inheritance:

ScopeBuilder Constants
~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: globus_sdk.scopes.data.AuthScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.FlowsScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.GroupsScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.NexusScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.SearchScopes
    :annotation:

.. note::

    ``TimersScopes`` is also available under the legacy name ``TimerScopes``.

.. autodata:: globus_sdk.scopes.data.TimersScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.TransferScopes
    :annotation:
