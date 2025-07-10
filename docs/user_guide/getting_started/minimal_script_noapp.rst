.. currentmodule:: globus_sdk

.. _minimal_script_noapp_tutorial:

How to Create A Minimal Script without GlobusApp
================================================

:class:`GlobusApp` provides a number of useful abstractions in the SDK.
It handles login flows and storage of tokens, coupled with later retrieval of
those tokens for use. It can keep track of which clients have been created and
registered with an app, and therefore make intelligent decisions about how and
when to prompt users to login.

New users should read :ref:`the guide for writing a minimal script
<minimal_script_tutorial>` before reading this doc.

:class:`GlobusApp` is built from several simpler components which can be used to
implement similar behaviors.
This doc covers how to write a simple script, but without using
:class:`GlobusApp`.

For readers who prefer to start with complete examples, jump ahead to these
sections before reviewing the doc:

-   :ref:`Login and List Groups (simple) <list_groups_noapp>`
-   :ref:`Login and List Groups (with storage) <list_groups_noapp_with_storage>`

Cases for not Using GlobusApp
-----------------------------

There are at least three main reasons to be interested in defining applications
without :class:`GlobusApp`:

1.  You have a use case which doesn't fit the behaviors of an app.
    e.g., Implementations of *APIs* or *services*.

2.  Any legacy codebase, predating :class:`GlobusApp`, will use the underlying
    constructs to implement login behaviors.

3.  Customizing and extending :class:`GlobusApp` to suit your use case may
    require understanding the underlying components.

.. note::

    Prior to the introduction of :class:`GlobusApp`, these tools were the only
    way that an application could be written with the ``globus_sdk``. If you
    are maintaining an existing application, you may need to be strategic about
    when and how to upgrade such usages.

Define an Auth Client Instance
------------------------------

In order to interact with Globus Auth, you will need a client object. This will
be the driver of the login flow.

.. code-block:: python

    import globus_sdk

    # this is the tutorial client ID
    # replace this string with your ID for production use
    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

    # create a client for interactions with Globus Auth
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)


This uses a :class:`NativeAppAuthClient`, which is one of the two types of client
object supporting logins. The other is :class:`ConfidentialAppAuthClient`,
which is for clients which authenticate themselves using a stored secret.

There are differences in behavior between the two types of Auth client, but
:class:`NativeAppAuthClient` is more appropriate for scripts which you may
later redistribute.

Login and Consent for Groups Access
-----------------------------------

In OAuth2, login flows are always driven through a web browser. In order to
connect our simple script to the browser context, we will go through a
challenge-response flow.
The script will print out a login URL. Upon logging in and returning to the
script, you paste in a verification code, which is then exchanged for tokens.

For simplicity, we'll print the login prompt to stdout and accept the
authorization code with a prompt for input.

Additionally, we will need to specify what scopes (what actions on what
services) we want access to in our script. This will drive the consent prompt
in the Globus Auth web interface.

.. code-block:: python

    # using that client, do a login flow for Globus Groups credentials
    auth_client.oauth2_start_flow(
        requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships
    )
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)


Create and Use a GroupsClient
-----------------------------

To make use of the tokens procured in the previous step, you'll need to create
a client object, pass it the appropriate token data, and use it to call out to
the Globus Groups API.

Credentials are passed through a generic "authorizer" interface which allows
the tokens to be passed statically or as a reference to some dynamic data
source.

.. code-block:: python

    # extract tokens from the response which match Globus Groups
    groups_tokens = tokens.by_resource_server[globus_sdk.GroupsClient.resource_server]

    # construct an AccessTokenAuthorizer and use it to construct the GroupsClient
    groups_client = globus_sdk.GroupsClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(groups_tokens["access_token"])
    )

    # call out to the Groups service to get a listing
    my_groups = groups_client.get_my_groups()

    # print in CSV format
    print("ID,Name,Roles")
    for group in my_groups:
        roles = "|".join({m["role"] for m in group["my_memberships"]})
        print(",".join([group["id"], f'"{group["name"]}"', roles]))

.. _list_groups_noapp:

Recap: List Groups Script
-------------------------

The previous sections can be combined into a working script.

*The following example is complete. It should run without modification "as-is".*

.. literalinclude:: list_groups_noapp.py
    :caption: ``list_groups_noapp.py`` [:download:`download <list_groups_noapp.py>`]
    :language: python

Adding in Refresh Tokens & Token Storage
----------------------------------------

To expand upon this example, it is possible to request long-lived tokens called
"refresh tokens", which are valid until they are revoked or go unused for a
long period.
Making use of refresh tokens is most appropriate if we also store the tokens
between runs of the script, so that we can reuse the tokens.

Refresh tokens operate by getting an access token, like the example above, but
allowing you to automatically replace or "refresh" that token any time it
expires. We will therefore also need to elaborate our usage to handle these
automatic refreshes.

Requesting Refresh Tokens
^^^^^^^^^^^^^^^^^^^^^^^^^

To request refresh tokens, simply pass ``refresh_tokens=True`` to the
``oauth2_start_flow`` call:

.. code-block:: python

    auth_client.oauth2_start_flow(
        requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships,
        refresh_tokens=True,
    )

Defining Token Storage
^^^^^^^^^^^^^^^^^^^^^^

Token storage abstractions are defined in the SDK which provide the ability to
read or write token data in a structured way.
Defining a token storage object is simple:

.. code-block:: python

    import os
    from globus_sdk.token_storage import JSONTokenStorage

    token_storage = JSONTokenStorage(
        os.path.expanduser("~/.list-my-globus-groups-tokens.json")
    )

Linking a Login Flow to Token Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To connect the tokens from login to a token storage, use the token storage
method ``store_token_response()`` at the end of the login flow.

And in order to make the script only prompt for login if there are no tokens,
we can ask the ``JSONTokenStorage.file_exists()`` method whether or not there
is a file.
This rewrites our login block to be nested under a ``file_exists()`` check:

.. code-block:: python

    # if there is no stored token file, we have not yet logged in
    if not token_storage.file_exists():
        # do a login flow, getting back a token response
        auth_client.oauth2_start_flow(
            requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships,
            refresh_tokens=True,
        )
        authorize_url = auth_client.oauth2_get_authorize_url()
        print(f"Please go to this URL and login:\n\n{authorize_url}\n")
        auth_code = input("Please enter the code here: ").strip()
        token_response = auth_client.oauth2_exchange_code_for_tokens(auth_code)
        # now store the tokens
        token_storage.store_token_response(token_response)

Building a RefreshTokenAuthorizer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Token storage defines how the data gets stored, and how it is retrieved.
The storage is also integral to how refresh tokens are used -- we need a place
to store updated tokens whenever we have a refresh.

We will load the groups token out of the token storage and use it to construct
a :class:`RefreshTokenAuthorizer`, which handles automatic refreshes. To write
updated tokens back into the storage, we pass it back into the authorizer, like
so:

.. code-block:: python

    # load the tokens from the storage -- either freshly stored or loaded from disk
    token_data = token_storage.get_token_data(globus_sdk.GroupsClient.resource_server)

    # construct the RefreshTokenAuthorizer which writes back to storage on refresh
    authorizer = globus_sdk.RefreshTokenAuthorizer(
        token_data.refresh_token,
        auth_client,
        access_token=token_data.access_token,
        expires_at=token_data.expires_at_seconds,
        on_refresh=token_storage.store_token_response,
    )

Construct and Use the GroupsClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have a new authorizer, it is simple to construct and use a new
client, just as before:

.. code-block:: python

    # use that authorizer to authorize the activity of the groups client
    groups_client = globus_sdk.GroupsClient(authorizer=authorizer)

    # call out to the Groups service to get a listing
    my_groups = groups_client.get_my_groups()

    # print in CSV format
    print("ID,Name,Roles")
    for group in my_groups:
        roles = "|".join({m["role"] for m in group["my_memberships"]})
        print(",".join([group["id"], f'"{group["name"]}"', roles]))

.. _list_groups_noapp_with_storage:

Recap: List Groups with RefreshTokens
-------------------------------------

As a complete example of the List Groups script with token storage and a
refresh token authorizer, the above sections can be combined into the following
script:

*The following example is complete. It should run without modification "as-is".*

.. literalinclude:: list_groups_noapp_with_storage.py
    :caption: ``list_groups_noapp_with_storage.py`` [:download:`download <list_groups_noapp_with_storage.py>`]
    :language: python
