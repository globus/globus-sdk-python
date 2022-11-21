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

Because the scopes for a token are associated with some concrete client which
will use that token, it makes sense to associate a scope with a client class.

The Globus SDK does this by providing the ``ScopeBuilder`` for a service as an
attribute of the client. For example,

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

MutableScope objects
--------------------

In order to support optional and dependent scopes, an additional type is
provided by ``globus_sdk.scopes``: the ``MutableScope`` class.

``MutableScope`` can be constructed directly or via a ``ScopeBuilder``'s
``make_mutable`` method, given a scope's short name.

For example, one can create a ``MutableScope`` from the Groups "all" scope
as follows:

.. code-block:: python

    from globus_sdk.scopes import GroupsScopes

    scope = GroupsScopes.make_mutable("all")

``MutableScope`` objects primarily provide two main pieces of functionality:
dynamically building a scope tree and serializing to a string.

Dynamic Scope Construction
~~~~~~~~~~~~~~~~~~~~~~~~~~

``MutableScope`` objects provide a tree-like interface for constructing scopes
and their dependencies.

For example, the transfer scope dependent upon a collection scope may be
constructed by means of ``MutableScope`` methods and the ``make_mutable`` method
of scope builders thusly:

.. code-block:: python

    from globus_sdk.scopes import GCSCollectionScopeBuilder, TransferScopes

    MAPPED_COLLECTION_ID = "...ID HERE..."

    # create the scopes with make_mutable
    transfer_scope = TransferScopes.make_mutable("all")
    data_access_scope = GCSCollectionScopeBuilder(MAPPED_COLLECTION_ID).make_mutable(
        "data_access", optional=True
    )
    # add data_access as a dependency
    transfer_scope.add_dependency(data_access_scope)

``MutableScope``\s can be used in most of the same locations where scope
strings can be used, but you can also call ``str()`` on them to get a
stringified representation.

Serializing Scopes
~~~~~~~~~~~~~~~~~~

Whenever scopes are being sent to Globus services, they need to be encoded as
strings. All mutabl scope objects support this by means of their defined
``serialize`` method. Note that ``__str__`` for a ``MutableScope`` is just an
alias for ``serialize``. For example, the following is valid usage to demonstrate
``str()``, ``repr()``, and ``serialize()``:

.. code-block:: pycon

    >>> from globus_sdk.scopes import MutableScope
    >>> foo = MutableScope("foo")
    >>> bar = MutableScope("bar")
    >>> bar.add_dependency("baz")
    >>> foo.add_dependency(bar)
    >>> print(str(MutableScope("foo")))
    foo[bar *baz]
    >>> print(bar.serialize())
    bar[baz]
    >>> alpha = MutableScope("alpha")
    >>> alpha.add_dependency(MutableScope("beta", optional=True))
    >>> print(repr(alpha))
    MutableScope("alpha", dependencies=[MutableScope("beta", optional=True)])

MutableScope Reference
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: MutableScope
    :members:
    :show-inheritance:

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

.. autodata:: globus_sdk.scopes.data.TimerScopes
    :annotation:

.. autodata:: globus_sdk.scopes.data.TransferScopes
    :annotation:
