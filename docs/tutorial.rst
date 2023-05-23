.. _tutorial:

Tutorial
========

.. _getting_started:

First Steps
-----------

This is a tutorial in the use of the Globus SDK. It takes you through a simple
step-by-step flow for registering your application, getting tokens, and using
them with our service.

These are the steps we will take:

#. :ref:`Create a Client <tutorial_step1>`
#. :ref:`Login and get tokens! <tutorial_step2>`
#. :ref:`Use tokens to access the service <tutorial_step3>`
#. :ref:`Explore the OAuthTokenResponse <tutorial_step4>`
#. :ref:`Do a login flow with Refresh Tokens <tutorial_step5>`
#. :ref:`Selected Examples <tutorial_step6>`

That should be enough to get you up and started.

Background on OAuth2 Clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Globus uses OAuth2 to handle authentication. In order to login, your
application must be registered with Globus Auth. This is called a "client" in
OAuth2, but Globus will also sometimes call this an "app".

If you plan to create your own application, you should create a new client by
following the instructions below. However, just for the purposes of this
tutorial, we have created a tutorial client which you may use.

.. _tutorial_step1:

Step 1: Create a Client
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    You can skip this section and jump right in by using the CLIENT_ID seen in
    the example code blocks below! That is the ID of the tutorial client, which
    lets you get started quickly and easily. Come back and create a client of
    your own when you're ready!

In order to complete an OAuth2 flow to get tokens, you must have a client or
"app" definition registered with Globus.

Navigate to the `Developer Site <https://developers.globus.org>`_ and select
"Register your app with Globus."
You will be prompted to login -- do so with the account you wish to use as your
app's administrator.

When prompted, create a Project. A Project is a collection of clients with a
shared list of administrators.
Projects let you share the administrative burden of a collection of apps.

In the "Add" menu for your Project, select "Add new app". To follow this
tutorial, we will specify several values you should use.

Enter the following pieces of information:

- **Native App**: Check this Box
- **Redirects**: https://auth.globus.org/v2/web/auth-code

and click "Create App".

.. warning::

    The **Native App** setting cannot be changed after a client is created.
    If it is not selected during creation, you must create a replacement client.

Expand the dropdown for the new app, and you should see an array of
attributes of your client.

You will need the Client ID from this screen.
Feel free to think of this as your App's "username".
You can hardcode it into scripts, store it in a config file, or even put it
into a database.
It's non-secure information and you can treat it as such.

In the rest of the tutorial we will assume in all code samples that it is
available in the variable, ``CLIENT_ID``.

.. _tutorial_step2:

Step 2: Login and get tokens!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Talking to Globus Services as a user requires that you authenticate to your new
App and get it Tokens, credentials proving that you logged into it and gave it
permission to access the service.

No need to worry about creating your own login pages and such -- for this type
of app, Globus provides all of that for you.
Run the following code sample to get your Access Tokens:

.. code-block:: python

    import globus_sdk

    # this is the tutorial client ID
    # replace this string with your ID for production use
    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    client.oauth2_start_flow()
    authorize_url = client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code you get after login here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    globus_auth_data = token_response.by_resource_server["auth.globus.org"]
    globus_transfer_data = token_response.by_resource_server["transfer.api.globus.org"]

    # most specifically, you want these tokens as strings
    AUTH_TOKEN = globus_auth_data["access_token"]
    TRANSFER_TOKEN = globus_transfer_data["access_token"]


The Globus SDK offers several features for managing credentials. The following components
are useful for further reading:

* :ref:`using GlobusAuthorizer objects <authorization>` handle passing tokens to Globus,
  and may handle token expiration

* :ref:`TokenStorage <tokenstorage>` objects handle storage of tokens

These are covered by several of the available :ref:`Examples <examples>` as
well.

.. _tutorial_step3:

Step 3: Use tokens to access the service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Continuing from the example above, you have two credentials to Globus Services
on hand: the ``AUTH_TOKEN`` and the ``TRANSFER_TOKEN``.

We'll focus on the ``TRANSFER_TOKEN`` for now. It's used to access the Tansfer
service.

.. _authorizer_first_use:

.. code-block:: python

    # a GlobusAuthorizer is an auxiliary object we use to wrap the token. In
    # more advanced scenarios, other types of GlobusAuthorizers give us
    # expressive power
    authorizer = globus_sdk.AccessTokenAuthorizer(TRANSFER_TOKEN)
    tc = globus_sdk.TransferClient(authorizer=authorizer)

    # high level interface; provides iterators for list responses
    print("My Endpoints:")
    for ep in tc.endpoint_search(filter_scope="my-endpoints"):
        print("[{}] {}".format(ep["id"], ep["display_name"]))


Note that the ``TRANSFER_TOKEN`` is only valid for a limited time. You'll have
to login again when it expires.


.. _advanced_tutorial:

Advanced Tutorial
-----------------

In the first steps of the Tutorial, we did a login flow to get an Access Token,
and used it. However, we didn't explain what that token is and how it works.

In this section, not only will we talk through more detail on Access Tokens, but
we'll also explore more advanced use cases and their near-cousins, Refresh Tokens.

.. _tutorial_step4:

Step 4: Explore the OAuthTokenResponse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the basic tutorial, we extracted an access token with these steps:

.. code-block:: python

    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    globus_transfer_data = token_response.by_resource_server["transfer.api.globus.org"]
    TRANSFER_TOKEN = globus_transfer_data["access_token"]

It's worth looking closer at the token response itself, as it is of particular
interest.

This is the ultimate product of the login flow, and it contains the credentials
resulting from login.

To recap, the whole flow can be done like so:

.. code-block:: python

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    client.oauth2_start_flow()
    authorize_url = client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

Though it has a few attributes and methods, by far the most important thing
about ``token_response`` to understand is
``token_response.by_resource_server``.

Let's take a look at ``str(token_response.by_resource_server)``:

.. code-block:: pycon

    >>> str(token_response.by_resource_server)
    {
      "auth.globus.org": {
        "access_token": "AQBX8YvVAAAAAAADxhAtF46RxjcFuoxN1oSOmEk-hBqvOejY4imMbZlC0B8THfoFuOK9rshN6TV7I0uwf0hb",
        "scope": "openid email profile",
        "token_type": "Bearer",
        "expires_at_seconds": 1476121216,
        "refresh_token": None
      },
      "transfer.api.globus.org": {
        "access_token": "AQBX8YvVAAAAAAADxg-u9uULMyTkLw4_15ReO_f2E056wLqjAWeLP51pgakLxYmyUDfGTd4SnYCiRjFq3mnj",
        "scope": "urn:globus:auth:scope:transfer.api.globus.org:all",
        "token_type": "Bearer",
        "expires_at_seconds": 1476121286,
        "refresh_token": None
      }
    }

The keys in the token response, ``"auth.globus.org"`` and ``"transfer.api.globus.org"``,
are the services which require tokens. These are the Resource Servers in the
response, and for each one, the response contains the following info:

- access_token: a credential which authenticates access to the Resource Server
- scope: a list of activities for which the access_token grants permissions
- token_type: the kind of authorization for which the token is used. All Globus
  tokens are sent as Bearer Auth headers
- expires_at_seconds: a POSIX timestamp for the time when the access_token
  expires
- refresh_token: a credential which can be used to replace or "refresh" the
  access_token when it expires. ``None`` unless explicitly requested.
  Details on refresh_token are in the next section

.. note::

    The keys into ``by_resource_server`` are the registered ``resource_server``
    value for the service.

    For Globus hosted services like Globus Auth and Globus Transfer, the
    ``resource_server`` is the hostname for the service, and can be retrieved
    via the ``resource_server`` class attribute for the relevant client.
    e.g., ``globus_sdk.TransferClient.resource_server``.

    For other services, including Globus Connect Server v5, the ``resource_server``
    value will be the ID of the service client. For Globus Connect Server v5, this
    is the ID of the Endpoint.

.. _tutorial_step5:

Step 5: Do a login flow with Refresh Tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As described above, there is enough code to do a login flow and get an Access
Token. However, that token will expire after a short duration, after which the
user will need to login again.

This can be avoided by requesting a Refresh Token, which is valid indefinitely
(unless revoked). The purpose of Refresh Tokens is to allow an application to
replace its Access Tokens without a fresh login.

The code above can easily include Refresh Tokens by modifying the call to
``oauth2_start_flow`` as follows:

.. code-block:: python

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    client.oauth2_start_flow(refresh_tokens=True)
    authorize_url = client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

If you peek at the ``token_response`` now, you'll see that the
``"refresh_token"`` fields are no longer nulled.

However, this only solves half of the problem. When should a new Access Token
be requested? The Globus SDK solves this problem for you with the
``GlobusAuthorizer`` objects :ref:`introduced above <authorizer_first_use>`.
The key is the :class:`RefreshTokenAuthorizer <globus_sdk.RefreshTokenAuthorizer>`
object, which handles refreshes.

Let's assume you want to do this with the :class:`TransferClient <globus_sdk.TransferClient>`.

.. code-block:: python

    # get credentials for the Globus Transfer service
    globus_transfer_data = token_response.by_resource_server["transfer.api.globus.org"]
    # the refresh token and access token are often abbreviated as RT and AT
    transfer_rt = globus_transfer_data["refresh_token"]
    transfer_at = globus_transfer_data["access_token"]
    expires_at_s = globus_transfer_data["expires_at_seconds"]

    # construct a RefreshTokenAuthorizer
    # note that `client` is passed to it, to allow it to do the refreshes
    authorizer = globus_sdk.RefreshTokenAuthorizer(
        transfer_rt, client, access_token=transfer_at, expires_at=expires_at_s
    )

    # and try using `tc` to make TransferClient calls. Everything should just
    # work -- for days and days, months and months, even years
    tc = globus_sdk.TransferClient(authorizer=authorizer)


With the above code, ``tc`` is a ``TransferClient`` which can authenticate
indefinitely, refreshing the Access Token whenever it expires.

.. _tutorial_step6:

Step 6: Selected Examples
~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`Minimal File Transfer Script <example_minimal_transfer>` provides a
  simple example of a file transfer

This example builds upon everything documented above. It will also include the
use of new features not covered by this tutorial. In particular, it will use
:ref:`the scopes module <scopes>` to provide scope strings as constants,
:class:`TransferData <globus_sdk.TransferData>` as a helper to construct a
transfer task document, and the ``requested_scopes`` argument to
``oauth2_start_flow`` (instead of the default scopes).

- The :ref:`Group Listing Script <example_group_listing>` provides a
  simple example of use of the Globus Groups service

Like the Minimal File Transfer Script, this example builds upon the tutorial,
specifying scopes. It demonstrates some simple output processing as well.
