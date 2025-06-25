Changed
-------

- The SDK's ``ScopeBuilder`` types have been replaced with
  ``StaticScopeCollection`` and ``DynamicScopeCollection`` types. (:pr:`NUMBER`)

  - Scopes provided as constants by the SDK are now ``Scope`` objects, not
    strings. They can be converted to strings trivially with ``str(scope)``.

  - The various scope builder types have been renamed. ``SpecificFlowScopes``,
    ``GCSEndpointScopes``, and ``GCSCollectionScopes`` replace
    ``SpecificFlowScopeBuilder``, ``GCSEndpointScopeBuilder``, and
    ``GCSCollectionScopeBuilder``.
