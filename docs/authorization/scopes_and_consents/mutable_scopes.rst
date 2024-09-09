.. _mutable_scopes:

.. currentmodule:: globus_sdk.scopes

MutableScopes
=============

.. warning::

    The ``MutableScope`` class and its interfaces are considered a legacy
    feature. They will be deprecated and removed in a future SDK release.

    Users should prefer to use ``globus_sdk.Scope`` instead.
    ``globus_sdk.Scope``, documented in :ref:`the scopes documentation <scopes>`,
    provides strictly more features and has a superior interface.

In order to support optional and dependent scopes, a type is
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
strings. All mutable scope objects support this by means of their defined
``serialize`` method. Note that ``__str__`` for a ``MutableScope`` is just an
alias for ``serialize``. For example, the following is valid usage to demonstrate
``str()``, ``repr()``, and ``serialize()``:

.. code-block:: pycon

    >>> from globus_sdk.scopes import MutableScope
    >>> foo = MutableScope("foo")
    >>> bar = MutableScope("bar")
    >>> bar.add_dependency("baz")
    >>> foo.add_dependency(bar)
    >>> print(str(foo))
    foo[bar[baz]]
    >>> print(bar.serialize())
    bar[baz]
    >>> alpha = MutableScope("alpha")
    >>> alpha.add_dependency(MutableScope("beta", optional=True))
    >>> print(str(alpha))
    alpha[*beta]
    >>> print(repr(alpha))
    MutableScope("alpha", dependencies=[MutableScope("beta", optional=True)])

MutableScope Reference
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: MutableScope
    :members:
    :show-inheritance:
