
Added
~~~~~

-   Added support for ``ScopeCollectionType`` to GlobusApp's ``__init__`` and
    ``add_scope_requirements`` methods. (:pr:`NUMBER`)

Changed
~~~~~~~

-   Updated ``ScopeCollectionType`` to be defined recursively. (:pr:`NUMBER`)


Development
~~~~~~~~~~~

-   Added a scope normalization function ``globus_sdk.scopes.scopes_to_scope_list`` to
    translate from ``ScopeCollectionType`` to a list of ``Scope`` objects.
    (:pr:`NUMBER`)

