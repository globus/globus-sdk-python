
Changed
~~~~~~~

-   The experimental ``GlobusApp`` construct's scope exploration interface has changed
    from ``app.get_scope_requirements(resource_server: str) -> tuple[Scope]`` to
    ``app.scope_requirements``. The new property will return a deep copy of the internal
    requirements dictionary mapping resource server to a list of Scopes. (:pr:`NUMBER`)

