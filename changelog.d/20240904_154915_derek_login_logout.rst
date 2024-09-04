
Added
~~~~~

-   Added ``login(...)``, ``logout(...)``, and ``login_required(...)`` to the
    experimental ``GlobusApp`` construct. (:pr:`NUMBER`)

    -   ``login(...)`` initiates a login flow if:

        -   the current entity requires a login to satisfy local scope requirements or
        -   ``auth_params``/``force=True`` is passed to the method.

    -   ``logout(...)`` remove and revokes the current entity's app-associated tokens.

    -   ``login_required(...)`` returns a boolean indicating whether the app believes
        a login is required to satisfy local scope requirements.

Removed
~~~~~~~

-   Made ``run_login_flow`` private in the experimental ``GlobusApp`` construct.
    Usage sites should be replaced with either ``app.login()`` or
    ``app.login(force=True)``. (:pr:`NUMBER`)

    -   **Old Usage**

        .. code-block:: python
            app = UserApp("my-app", client_id="<my-client-id>")
            app.run_login_flow()

    -   **New Usage**

        .. code-block:: python
            app = UserApp("my-app", client_id="<my-client-id>")
            app.login(force=True)
