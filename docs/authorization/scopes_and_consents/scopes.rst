.. _scopes:

.. currentmodule:: globus_sdk.scopes

Scopes
======

The SDK provides a ``Scope`` object which is the class model for a scope.
``Scope``\s can be parsed from strings and serialized to strings, and support
programmatic manipulations to describe dependent scopes.

``Scope`` can be constructed using its initializer, via ``Scope.parse``, or via
:meth:`ScopeParser.parse`.

For example, one can create a ``Scope`` object for the OIDC ``openid`` scope:

.. code-block:: python

    from globus_sdk.scopes import Scope

    openid_scope = Scope("openid")

``Scope`` objects primarily provide three main pieces of functionality:

    * deserializing (parsing a single scope)
    * serializing (stringifying)
    * scope tree construction

Tree Construction
~~~~~~~~~~~~~~~~~

``Scope`` objects provide a tree-like interface for constructing scopes
and their dependencies.
Because ``Scope`` objects are immutable, trees are constructed by building new
scopes.

For example, the transfer scope dependent upon a collection scope may be
constructed by means of ``Scope`` methods thusly:

.. code-block:: python

    from globus_sdk.scopes import GCSCollectionScopeBuilder, TransferScopes, Scope

    MAPPED_COLLECTION_ID = "...ID HERE..."

    # create the scope object, and get the data_access_scope as a string
    data_access_scope = GCSCollectionScopeBuilder(MAPPED_COLLECTION_ID).data_access
    # add data_access as an optional dependency
    transfer_scope = TransferScopes.all.with_dependency(data_access_scope, optional=True)

``Scope``\s can be used in most of the same locations where scope
strings can be used, but you can also call ``str(scope)`` to get a
stringified representation.

Serializing Scopes
~~~~~~~~~~~~~~~~~~

Whenever scopes are being sent to Globus services, they need to be encoded as
strings. All scope objects support this by means of their defined
``__str__`` method. For example, the following is an example of
``str()`` and ``repr()`` usage:

.. code-block:: pycon

    >>> from globus_sdk.scopes import Scope
    >>> foo = Scope("foo")
    >>> bar = Scope("bar")
    >>> bar = bar.with_dependency(Scope("baz"))
    >>> foo = foo.with_dependency(bar)
    >>> print(str(foo))
    foo[bar[baz]]
    >>> print(str(bar))
    bar[baz]
    >>> alpha = Scope("alpha")
    >>> alpha = alpha.with_dependency("beta", optional=True)
    >>> print(str(alpha))
    alpha[*beta]
    >>> print(repr(alpha))
    Scope("alpha", dependencies=[Scope("beta", optional=True)])

Reference
~~~~~~~~~

.. autoclass:: Scope
   :members:
   :member-order: bysource
