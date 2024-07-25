
.. _using_globus_app:

.. py:currentmodule:: globus_sdk.experimental.globus_app

Using a GlobusApp
=================

Programmatic communication with Globus services relies on the authorization of requests.
Management and resolution of this authorization can become an arduous task, especially
when a script needs to interact with different services each carrying an individual set
of complex auth requirements. To assist with this task, this library provides a utility
construct called a GlobusApp.

A :py:class:`~GlobusApp` is a distinct object which will manage auth requirements
(i.e. **scopes**) identified by their associated service (i.e. **resource server**).
In addition to storing these requirements, a GlobusApp provides a mechanism to resolve
unmet ones through browser and api-based auth flows, supplying the resulting tokens to
bound clients as requested.

There are two flavors of GlobusApp:

*   :py:class:`~UserApp`, a GlobusApp for interactions between an end user and Globus
    services. Facilitates interactions *on behalf of a user*.

*   :py:class:`~ClientApp`, a GlobusApp for interactions between a client
    (i.e. service account) and Globus services. Facilitates interactions
    *as the script itself*.

Setup
-----

A GlobusApp is heavily configurable object. For common scripting usage however,
instantiation only requires two parameters:

#.  **App Name** - A human readable slug to identify your app in http requests and token
    caches.

#.  **Client Info** - either a *Native Client's* ID or a *Confidential Client's* ID and
    secret pair.

    *   There are important distinctions to consider when choosing your client type; see
        `Developing an Application Using Globus Auth <https://docs.globus.org/api/auth/developer-guide/#developing-apps>`_.

        For a simplified heuristic however:

        *   Use a *Confidential Client* when your client needs to own cloud resources
            itself and will be used in a trusted environment where you can securely
            hold a secret.

        *   Use a *Native Client* when your client will be facilitating interactions
            between a user and a service, particularly if it is bundled within a
            script or cli tool to be distributed to end-user's machines.


..  Note::

    Even in the context of a UserApp, client info is required to interact with a
    service. Those interactions will be performed on behalf of a user instead of the
    client itself, but the client is necessary to facilitate the interaction.


Once instantiated, an app can be passed to any service client using the init
``app`` kwarg (e.g. ``TransferClient(app=my_app)``). Doing this will bind the app to the
client, registering a default set of scopes requirements for the service client's
resource server and configuring the app as the service client's auth provider.


..  tab-set::

    ..  tab-item:: UserApp

        Construct a UserApp then bind it to a transfer client and a flows client.

        ..  Note::

            ``UserApp.__init__(...)`` also accepts a `client_secret` kwarg which must be
            supplied for confidential clients.

        ..  code-block:: python

            import globus_sdk
            from globus_sdk.experimental.globus_app import UserApp

            CLIENT_ID = "..."
            my_app = UserApp("my-user-app", client_id=CLIENT_ID)

            transfer_client = globus_sdk.TransferClient(app=my_app)
            flows_client = globus_Sdk.FlowsClient(app=my_app)


    .. tab-item:: ClientApp

        Construct a ClientApp then bind it to a transfer client and flows_client.

        ..  Note::

            ``ClientApp.__init__(...)`` does not allow omission of the `client_secret`
            kwarg as native clients are not allowed.

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

From this point, the app manages scope validation, token caching, and authorizer
supply for any the clients it is bound to.

In the above example, listing a client's or user's flows becomes as simple as:

..  code-block:: python

    flows = flows_client.list_flows()["flows"]

If cached tokens are missing, expired, or otherwise insufficient (e.g. the first time
you run the script), the app will automatically initiate an auth flow to acquire new
tokens. For a UserApp, this will print out a URL to terminal with a prompt instructing a
the user to follow the link and enter the code they're given back into the terminal. For
a ClientApp, the app will retrieve tokens programmatically through an Auth API.

Once this auth flow has finished, the app will cache tokens for future use and
invocation of your requested method will proceed as expected.


Manually Running Login Flows
----------------------------

While your app will automatically initiate and oversee auth flows as detected, sometimes
the programmer knows timing better. To manually trigger a login flow, call
``GlobusApp.run_login_flow(...)``. This will initiate a flow requesting new tokens
based on the app's currently defined scope requirements, caching the resulting tokens
for future use.

This method accepts a single optional parameter, ``auth_params``, where a caller
may specify additional session-based auth parameters such as requiring the use of an
mfa token or rendering with a specific message:


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

Globus service clients all maintain as a part of their class definition a list of
default scope requirements to be attached to any bound app. These scopes represent our
best approximation of a "standard set" for this service; unfortunately however,
this list will note be sufficient for all use cases.

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
    scope. Neither default scope (``flows:view_flows`` and ``flows:run_status``) are
    registered.

#.  Through a service client's ``add_app_scope`` method.

    ..  code-block:: python

        from globus_sdk import Scope, FlowsClient

        flows_client = FlowsClient(app=my_app)
        flows_client.add_app_scope(Scope(FlowsClient.scopes.manage_flows))

    This approach will add the ``flows:manage_flows`` scope to the app's existing set of
    scopes. Since ``app_scopes`` was omitted in the client initialization, the default
    scopes are registered as well.
