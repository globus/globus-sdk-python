
Fixed
~~~~~

-   Fixed a bug where upgrading from access token to refresh token mode in a
    ``GlobusApp`` could result in multiple login prompts. (:pr:`NUMBER`)

Removed
~~~~~~~

-   Removed the ``skip_error_handling`` optional kwarg from the method interface
    ``GlobusApp.get_authorizer(...)``. (:pr:`NUMBER`)
