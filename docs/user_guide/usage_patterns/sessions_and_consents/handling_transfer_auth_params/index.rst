.. _userguide_handle_transfer_auth_params:

Handling Authorization Parameters from a Transfer Operation
===========================================================

Globus Transfer interacts with Collections and their underlying Endpoints both
synchronously and asynchronously.

The example below demonstrates a synchronous interaction -- ``ls`` on a
collection -- with handling for the possibility that a session-related error is
returned.
The session error can be parsed into a Globus Auth Requirements Error document
-- a :class:`globus_sdk.gare.GARE` -- via ``globus_sdk.gare``.
Once the error is recognized, the parameters parsed from it can be fed back
into a login flow.
Doing so will update the user's session, resolving the issue.

Creating a Test Collection
--------------------------

In order to test this sample script in full, you will need a collection with a
session policy which requires users to login with a specific ID or within a
certain time period.
The following section covers a recommended test collection configuration.
This will require administrative access to a Globus Connect Server endpoint.

.. note::

    Globus tutorial resources do not contain session policies, making them
    easier to use.
    However, this means they are not suitable for the example script given
    below.
    Tutorial collections will work, but they will not demonstrate the
    interesting features in use.

Create a POSIX Storage Gateway With a Timeout Policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On a Globus Connect Server Endpoint which you administer, create a new Storage
Gateway with a policy explicitly designed for testing.
The gateway will need the following properties, with the following recommended
values:

- gateway type: ``posix``
- display name: ``sdk-test-policy``
- root path: ``/``
- domain requirements: require a domain in which you have an identity
- authentication timeout in minutes: 1

You can create a gateway with a command like the following, which uses the
``uchicago.edu`` domain as an example:

.. code-block:: bash

    globus-connect-server storage-gateway create posix \
        sdk-test-gateway --authentication-timeout-mins 1 \
        --domain uchicago.edu

Record the storage gateway ID:

.. code-block:: bash

    STORAGE_GATEWAY_ID="..."

Using a one minute timeout will make the session handling very easy to test.
Simply interact with the collection, wait one minute, and then try using it
again -- you should be prompted to log in a second time to meet the timeout
requirement.

.. tip::

    You do not need to be an administrator for the domain you set, but you do
    need an identity from that domain.
    You are setting a policy for your Storage Gateway with this setting to
    require identities from that domain.

    If you don't have a ``uchicago.edu`` identity, you could create a gateway
    like the example, but you wouldn't be able to use it!

Create a Mapped Collection on that Gateway
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Storage Gateway encodes the requisite policy.
No special configuration is needed for the mapped collection used for testing.
Simply create a collection on the test gateway, e.g.:

.. code-block:: bash

    globus-connect-server collection create \
        "$STORAGE_GATEWAY_ID" / sdk-test-collection

Note the collection ID, we will need it in the following steps.

Run ``ls`` on the Collection
----------------------------

Running a simple ``ls`` on this collection is no different from doing so on any
other collection.
We have setup a 1 minute timeout for the test collection, so this will likely
work the first time that it runs.

.. code-block:: python

    import globus_sdk

    # this is the SDK tutorial client ID, replace with your own ID
    NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    # set the collection ID to your test collection
    COLLECTION_ID = "..."

    with globus_sdk.UserApp("ls-session", client_id=NATIVE_CLIENT_ID) as app:
        client = globus_sdk.TransferClient(app=app)

        # because the recommended test configuration uses a mapped collection
        # without High Assurance capabilities, it will have a data_access scope
        # requirement
        # comment out this line if your collection does not use data_access
        client.add_app_data_access_scope(COLLECTION_ID)

        ls_result = client.operation_ls(COLLECTION_ID)
        for item in ls_result:
            name = item["name"]
            if item["type"] == "dir":
                name += "/"
            print(name)

Run Again, Observe the Session Error
------------------------------------

The 1 minute timeout guarantees that we can trivially produce a session timeout
error by waiting one minute and running the script again.
You should see a stacktrace like the following:

.. code-block:: text

    Traceback (most recent call last):
      File "/home/demo-user/ls_session.py", line 18, in <module>
        ls_result = client.operation_ls(COLLECTION_ID)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/demo-user/.venv/lib/python3.2/globus_sdk/services/transfer/client.py", line 1286, in operation_ls
        self.get(f"operation/endpoint/{endpoint_id}/ls", query_params=query_params)
      File "/home/demo-user/.venv/lib/python3.2/globus_sdk/client.py", line 273, in get
        return self.request(
               ^^^^^^^^^^^^^
      File "/home/demo-user/.venv/lib/python3.2/globus_sdk/client.py", line 461, in request
        raise self.error_class(r)
    globus_sdk.services.transfer.errors.TransferAPIError: ('GET', 'https://transfer.api.globus.org/v0.10/operation/endpoint/2a0d28b8-d2a3-4143-9f76-93ab09497b85/ls', 'Bearer', 502, 'ExternalError.DirListingFailed.LoginFailed', 'Command Failed: Error (login)\nEndpoint: uc-restricted-col (2a0d28b8-d2a3-4143-9f76-93ab09497b85)\nServer: 44.201.14.78:443\nMessage: Login Failed\n---\nDetails: 530-Login incorrect. : GlobusError: v=1 c=LOGIN_DENIED\\r\\n530-GridFTP-Message: None of your authenticated identities are from domains allowed by resource policies\\r\\n530-GridFTP-JSON-Result: {"DATA_TYPE": "result#1.1.0", "authorization_parameters": {"session_required_single_domain": ["uchicago.edu"]}, "code": "permission_denied", "detail": {"DATA_TYPE": "not_from_allowed_domain#1.0.0", "allowed_domains": ["uchicago.edu"]}, "has_next_page": false, "http_response_code": 403, "message": "None of your authenticated identities are from domains allowed by resource policies"}\\r\\n530 End.\\r\\n\n', '7U5dNqzDn')

The exact details will vary, but the primary content of the error is that you
do not satisfy the session requirements of the collection.

Parse the Error and Confirm ``authorization_parameters`` are present
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Handling and parsing this error requires that we add an exception handler.
To enhance readability, we will wrap the ``ls`` operation in a function.

The caught exception will have an ``info`` property with populated
``authorization_parameters``.
We can check for this easily:

.. code-block:: python

    import globus_sdk

    # this is the SDK tutorial client ID, replace with your own ID
    NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    # set the collection ID to your test collection
    COLLECTION_ID = "..."


    def print_ls_data(client):
        ls_result = client.operation_ls(COLLECTION_ID)
        for item in ls_result:
            name = item["name"]
            if item["type"] == "dir":
                name += "/"
            print(name)


    with globus_sdk.UserApp("ls-session", client_id=NATIVE_CLIENT_ID) as app:
        client = globus_sdk.TransferClient(app=app)

        # because the recommended test configuration uses a mapped collection
        # without High Assurance capabilities, it will have a data_access scope
        # requirement
        # comment out this line if your collection does not use data_access
        client.add_app_data_access_scope(COLLECTION_ID)

        # do the `ls` and detect the authorization_parameters as being present
        try:
            print_ls_data()
        except globus_sdk.TransferAPIError as err:
            if err.info.authorization_parameters:
                print("An authorization requirement was not met.")
            else:
                raise

Convert the Error to GARE Format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Globus Auth Requirements Errors ("GAREs") are a standardized format for
Globus Auth session information to be passed between components.
When these ``authorization_parameters`` errors are encountered, they can be
converted to the GARE format using the tooling in ``globus_sdk.gare``:

.. code-block:: python

    import globus_sdk.gare

    try:
        print_ls_data(client)
    except globus_sdk.TransferAPIError as err:
        if err.info.authorization_parameters:
            print("An authorization requirement was not met.")
            gare = globus_sdk.gare.to_gare(err)
            print("GARE data:", str(gare))
        else:
            raise


Redrive Logins with the Parsed Authorization Params
---------------------------------------------------

Now that we have the data parsed into GARE format, it is relatively simple to
pass the parsed ``authorization_parameters`` data to a login flow.
Because the underlying requirement in this case is a new login flow, we must
also set ``prompt=login`` in the parameters.

Having done so, we can repeat the login step using that information:

.. code-block:: python

    try:
        print_ls_data(client)
    except globus_sdk.TransferAPIError as err:
        if err.info.authorization_parameters:
            print("An authorization requirement was not met. Logging in again...")

            gare = globus_sdk.gare.to_gare(err)
            params = gare.authorization_parameters
            # set 'prompt=login', which guarantees a fresh login without
            # reliance on the browser session
            params.prompt = "login"

            # pass these parameters into a login flow
            USER_APP.login(auth_params=params)
        else:
            raise


Summary: Complete Example
-------------------------

Combining the pieces above, we can construct a working complete example script.
A collection with session requirements is needed in order to demonstrate
the behavior.

.. literalinclude:: ls_with_session_handling.py
    :caption: ``ls_with_session_handling.py`` [:download:`download <ls_with_session_handling.py>`]
    :language: python
