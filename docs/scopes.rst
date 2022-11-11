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

Scope objects
-------------

In order to support optional and dependent scopes, an additional type is
provided by ``globus_sdk.scopes``: the ``Scope`` class.

``Scope`` can be constructed directly, from full scope strings, or via a
``ScopeBuilder``'s ``make_mutable`` method, given a scope's short name.

For example, one can create a ``Scope`` from the Groups "all" scope as
follows:

.. code-block:: python

    from globus_sdk.scopes import GroupsScopes

    scope = GroupsScopes.make_mutable("all")

``Scope`` objects primarily provide three main pieces of functionality:
parsing from a string, dynamically building a scope tree, and serializing to a
string.

Scope Parsing
~~~~~~~~~~~~~

:meth:`Scope.parse` is the primary parsing method. Given a string, parsing may
produce a list of scopes. The reason for this is that a scope string being
requested may be a space-delimited set of scopes. For example, the following
parse is desirable:

.. code-block:: pycon

    >>> Scope.parse("openid urn:globus:auth:scopes:transfer.api.globus.org:all")
    [
      Scope("openid"),
      Scope("urn:globus:auth:scopes:transfer.api.globus.org:all"),
    ]

Additionally, scopes can be deserialized from strings with
:meth:`Scope.deserialize`. This is similar to ``parse``, but it must return
exactly one scope. For example,

.. code-block:: pycon

    >>> Scope.deserialize("urn:globus:auth:scopes:transfer.api.globus.org:all")
    Scope("urn:globus:auth:scopes:transfer.api.globus.org:all")

Parsing supports scopes with dependencies and optional scopes denoted by the
``*`` marker. Therefore, the following is also a valid parse:

.. code-block:: pycon

    >>> transfer_scope = "urn:globus:auth:scopes:transfer.api.globus.org:all"
    >>> collection_scope = (
    ...     "https://auth.globus.org/scopes/c855676f-7840-4630-9b16-ef260aaf02c3/data_access"
    ... )
    >>> Scope.deserialize(f"{transfer_scope}[*{collection_scope}]")
    Scope(
      "urn:globus:auth:scopes:transfer.api.globus.org:all",
      dependencies=[
        Scope(
          "https://auth.globus.org/scopes/c855676f-7840-4630-9b16-ef260aaf02c3/data_access",
          optional=True
        )
      ]
    )

Dynamic Scope Construction
~~~~~~~~~~~~~~~~~~~~~~~~~~

In the parsing example above, a scope string was constructed as a format string
which was then parsed into a complex dependent scope structure. This can be
done directly, without needing to encode the scope as a string beforehand.

For example, the same transfer scope dependent upon a collection scope may be
constructed by means of ``Scope`` methods and the ``make_mutable`` method of
scope builders:

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

``Scope``\s can be used in most of the same locations where scope
strings can be used, but you can also call ``str()`` on them to get a
stringified representation.

Serializing Scopes
~~~~~~~~~~~~~~~~~~

Whenever scopes are being sent to Globus services, they need to be encoded as
strings. All scope objects support this by means of their defined ``serialize``
method. Note that ``__str__`` for a ``Scope`` is just an alias for
``serialize``. For example, the following is valid usage to demonstrate
``str()``, ``repr()``, and ``serialize()``:

.. code-block:: pycon

    >>> from globus_sdk.scopes import Scope
    >>> foo = Scope("foo")
    >>> bar = Scope("bar")
    >>> bar.add_dependency("baz")
    >>> foo.add_dependency(bar)
    >>> print(str(Scope("foo")))
    foo[bar *baz]
    >>> print(bar.serialize())
    bar[baz]
    >>> alpha = Scope("alpha")
    >>> alpha.add_dependency("*beta")
    >>> print(repr(alpha))
    Scope("alpha", dependencies=[Scope("beta", optional=True)])

Scope Reference
~~~~~~~~~~~~~~~

.. autoclass:: Scope
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
