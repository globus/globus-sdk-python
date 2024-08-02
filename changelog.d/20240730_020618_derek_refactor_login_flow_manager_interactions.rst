
Changed
~~~~~~~

-   Changed the experimental ``GlobusApp`` class in the following ways (:pr:`NUMBER`):

    -   ``LoginFlowManagers`` now insert ``GlobusApp.app_name`` into any native
        client login flows as the ``prefill_named_grant``.

    -   ``GlobusAppConfig`` now accepts a ``login_redirect_uri`` parameter to specify
        the redirect URI for a login flow.

        -   Invalid when used with a ``LocalServerLoginFlowManager``.

        -   Defaults to ``"https://auth.globus.org/v2/web/auth-code"`` for native
            client flows. Raises an error if not set for confidential ones.

    -   ``UserApp`` now allows for the use of confidential client flows with the use of
        either a ``LocalServerLoginFlowManager`` or a configured ``login_redirect_uri``.

    -   ``GlobusAppConfig.login_flow_manager`` now accepts shorthand string references
        ``"command-line"`` to use a ``CommandLineLoginFlowManager`` and
        ``"local-server"`` to use a ``LocalServerLoginFlowManager``.

    -   ``GlobusAppConfig.login_flow_manager`` also now accepts a
        ``LoginFlowManagerProvider``, a class with a
        ``for_globus_app(...) -> LoginFlowManager`` class method.


