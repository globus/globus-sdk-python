
Changed
~~~~~~~

-   Added a contextmanager to ensure that the call to ``GlobusApp.get_authorizer(...)``
    only ever calls the registered ``token_validation_error_handler`` once, even if
    nested calls happen as a part of the method invocation. (:pr:`NUMBER`)
