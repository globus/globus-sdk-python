.. _scope_parsing:

.. currentmodule:: globus_sdk.scopes

Scope Parsing
=============

Scope parsing is handled by the :class:`ScopeParser` type.

Additionally, :class:`Scope` objects define a
:meth:`parse() <globus_sdk.scopes.Scope.parse>` method which wraps parser
usage.

:class:`ScopeParser` provides classmethods as its primary interface, so there
is no need to instantiate the parser in order to use it.

ScopeParser Reference
---------------------

.. autoclass:: ScopeParser
    :members:
    :show-inheritance:

.. autoclass:: ScopeParseError

.. autoclass:: ScopeCycleError

.. rubric:: Utility Functions

``globus_sdk.scopes`` also provides helper functions which are used to
manipulate scope objects.

.. autofunction:: scopes_to_str

.. autofunction:: scopes_to_scope_list
