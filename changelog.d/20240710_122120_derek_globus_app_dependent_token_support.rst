
Fixed
~~~~~

- ``GlobusApp.add_scope_requirements`` now has the side effect of clearing the
  authorizer cache for any referenced resource servers. (:pr:`NUMBER`)
- ``GlobusAuthorizer.scope_requirements`` was made private and a new method for
  accessing scope requirements was added at ``GlobusAuthorizer.get_scope_requirements``.
  (:pr:`NUMBER`)
- A ``GlobusApp`` will now auto-create an Auth consent client for dependent scope
  evaluation against consents as a part of instantiation. (:pr:`NUMBER`)
