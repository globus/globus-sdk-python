
.. _using_globus_app:

.. py:currentmodule:: globus_sdk.experimental.globus_app

Using a GlobusApp
=================

Programmatic communication with Globus services relies on the authorization of requests.
Management and resolution of this authorization can become an arduous task, especially
when a script needs to interact with different services each carrying an individual set
of complex authentication and authorization requirements. To assist with this task, this
library provides a utility construct called a GlobusApp.

A :py:class:`~GlobusApp` is a distinct object which will manage Globus Auth requirements
(i.e., **scopes**) identified by their associated service (i.e., **resource server**).
In addition to storing them, a GlobusApp provides a mechanism to resolve unmet
requirements through browser- and API-based authorization flows, supplying the resulting
tokens to bound clients as requested.

There are two flavors of GlobusApp:

*   :py:class:`~UserApp`, a GlobusApp for interactions between an end user and Globus
    services. Operations are performed as a *user identity*.

*   :py:class:`~ClientApp`, a GlobusApp for interactions between a client
    (i.e. service account) and Globus services. Operations are performed as a
    *client identity*.

Setup
-----

A GlobusApp is a heavily configurable object. For common scripting usage however,
instantiation only requires two parameters:

#.  **App Name** - A human readable name to identify your app in HTTP requests and token
    caching (e.g., "My Cool Weathervane").

#.  **Client Info** - either a *Native Client's* ID or a *Confidential Client's* ID and
    secret pair.

    *   There are important distinctions to consider when choosing your client type; see
        `Developing an Application Using Globus Auth <https://docs.globus.org/api/auth/developer-guide/#developing-apps>`_.

        A simplified heuristic to help choose the client type however is:

        *   Use a *Confidential Client* when your client needs to own cloud resources
            itself and will be used in a trusted environment where you can securely
            hold a secret.

        *   Use a *Native Client* when your client will be facilitating interactions
            between a user and a service, particularly if it is bundled within a
            script or cli tool to be distributed to end-users' machines.


    ..  Note::

        Both UserApps and ClientApps require a client.

        In a UserApp, the client sends requests representing a user identity; whereas in
        a ClientApp, the requests represent the client identity itself.


Once instantiated, a GlobusApp can be passed to any service client using the init
``app`` keyword argument (e.g. ``TransferClient(app=my_app)``). Doing this will bind the
app to the client, registering a default set of scopes requirements for the service
client's resource server and configuring the app as the service client's auth provider.


..  tab-set::

    ..  tab-item:: UserApp

        Construct a UserApp then bind it to a Transfer client and a Flows client.

        ..  Note::

            ``UserApp.__init__(...)`` currently only supports Native clients.
            Confidential client support is forthcoming.

        ..  code-block:: python

            import globus_sdk
            from globus_sdk.experimental.globus_app import UserApp

            CLIENT_ID = "..."
            my_app = UserApp("my-user-app", client_id=CLIENT_ID)

            transfer_client = globus_sdk.TransferClient(app=my_app)
            flows_client = globus_sdk.FlowsClient(app=my_app)


    .. tab-item:: ClientApp

        Construct a ClientApp, then bind it to a Transfer client and a Flows client.

        ..  Note::

            ``ClientApp.__init__(...)`` requires the `client_secret` keyword argument.
            Native clients, which lack secrets, are not allowed.

        ..  code-block:: python

            import globus_sdk
            from globus_sdk.experimental.globus_app import ClientApp

            CLIENT_ID = "..."
            CLIENT_SECRET = "..."
            my_app = ClientApp("my-client-app", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

            transfer_client = globus_sdk.TransferClient(app=my_app)
            flows_client = globus_sdk.FlowsClient(app=my_app)


Usage
-----

From this point, the app manages scope validation, token caching and routing for any
bound clients.

In the above example, listing a client's or user's flows becomes as simple as:

..  code-block:: python

    flows = flows_client.list_flows()["flows"]

If cached tokens are missing, expired, or otherwise insufficient (e.g., the first time
you run the script), the app will automatically initiate an auth flow to acquire new
tokens. With a UserApp, the app will print a URL to the terminal with a prompt
instructing a the user to follow the link and enter the code they're given back into the
terminal. With a ClientApp, the app will retrieve tokens programmatically through a
Globus Auth API.

Once this auth flow has finished, the app will cache tokens for future use and
invocation of your requested method will proceed as expected.


Manually Running Login Flows
----------------------------

While your app will automatically initiate and oversee auth flows as detected, sometimes
an author may want to explicitly control when an authorization occurs. To manually
trigger a login flow, call ``GlobusApp.run_login_flow(...)``. This will initiate an auth
flow requesting new tokens based on the app's currently defined scope requirements, and
caching the resulting tokens for future use.

This method accepts a single optional parameter, ``auth_params``, where a caller
may specify additional session-based auth parameters such as requiring the use of an
MFA token or rendering with a specific message:


..  code-block:: python

    from globus_sdk.experimental.auth_requirements_error import GlobusAuthorizationParameters

    ...

    my_app.run_login_flow(
        auth_params=GlobusAuthorizationParameters(
            session_message="Please authenticate with MFA",
            session_required_mfa=True,
        )
    )


Manually Defining Scope Requirements
------------------------------------

Globus service client classes all maintain an internal list of default scope
requirements to be attached to any bound app. These scopes represent an approximation of
a "standard set" for each service. This list however is not sufficient for all use
cases.

For example, the FlowsClient defines its default scopes as ``flows:view_flows`` and
``flows:run_status`` (read-only access). These scopes will not be sufficient for a
script which needs to create new flows or modify existing ones. For that script, the
author must manually attach the ``flows:manage_flows`` scope to the app.

This can be done in one of two ways:

#.  Through a service client initialization, using the ``app_scopes`` kwarg.

    ..  code-block:: python

        from globus_sdk import Scope, FlowsClient

        FlowsClient(app=my_app, app_scopes=[Scope(FlowsClient.scopes.manage_flows)])

    This approach results in an app which only requires the ``flows:manage_flows``
    scope. The default scopes (``flows:view_flows`` and ``flows:run_status``) are not
    registered.

#.  Through a service client's ``add_app_scope`` method.

    ..  code-block:: python

        from globus_sdk import FlowsClient

        flows_client = FlowsClient(app=my_app)
        flows_client.add_app_scope(FlowsClient.scopes.manage_flows)

    This approach will add the ``flows:manage_flows`` scope to the app's existing set of
    scopes. Since ``app_scopes`` was omitted in the client initialization, the default
    scopes are registered as well.
