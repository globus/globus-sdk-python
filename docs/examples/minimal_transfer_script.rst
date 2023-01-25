.. _example_minimal_transfer:

Minimal File Transfer Script
----------------------------

The following is an extremely minimal script to demonstrate a file transfer
using the :class:`TransferClient <globus_sdk.TransferClient>`.

It uses the tutorial client ID from the :ref:`tutorial <tutorial>`.
For simplicity, the script will prompt for login on each use.

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    # requested_scopes specifies a list of scopes to request
    # instead of the defaults, only request access to the Transfer API
    auth_client.oauth2_start_flow(requested_scopes=TransferScopes.all)
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

    # construct an AccessTokenAuthorizer and use it to construct the
    # TransferClient
    transfer_client = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
    )

    # Globus Tutorial Endpoint 1
    source_endpoint_id = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
    # Globus Tutorial Endpoint 2
    dest_endpoint_id = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"

    # create a Transfer task consisting of one or more items
    task_data = globus_sdk.TransferData(
        source_endpoint=source_endpoint_id, destination_endpoint=dest_endpoint_id
    )
    task_data.add_item(
        "/share/godata/file1.txt",  # source
        "/~/minimal-example-transfer-script-destination.txt",  # dest
    )

    # submit, getting back the task ID
    task_doc = transfer_client.submit_transfer(task_data)
    task_id = task_doc["task_id"]
    print(f"submitted transfer, task_id={task_id}")


Minimal File Transfer Script Handling ConsentRequired
-----------------------------------------------------

The above example works with certain endpoint types, but will fail if either
the source or destination endpoint requires a ``data_access`` scope. This
requirement will cause the Transfer submission to fail with a
``ConsentRequired`` error.

The example below catches the ``ConsentRequired`` error and retries the
submission after a second login.

This kind of "reactive" handling of ``ConsentRequired`` is the simplest
strategy to design and implement.

We'll also enhance the example to take endpoint IDs from the command line.

.. code-block:: python

    import argparse
    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    parser = argparse.ArgumentParser()
    parser.add_argument("SRC")
    parser.add_argument("DST")
    args = parser.parse_args()

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    # we will need to do the login flow potentially twice, so define it as a
    # function
    #
    # we default to using the Transfer "all" scope, but it is settable here
    # look at the ConsentRequired handler below for how this is used
    def login_and_get_transfer_client(*, scopes=TransferScopes.all):
        auth_client.oauth2_start_flow(requested_scopes=scopes)
        authorize_url = auth_client.oauth2_get_authorize_url()
        print(f"Please go to this URL and login:\n\n{authorize_url}\n")

        auth_code = input("Please enter the code here: ").strip()
        tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
        transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

        # return the TransferClient object, as the result of doing a login
        return globus_sdk.TransferClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
        )


    # get an initial client to try with, which requires a login flow
    transfer_client = login_and_get_transfer_client()

    # create a Transfer task consisting of one or more items
    task_data = globus_sdk.TransferData(
        source_endpoint=args.SRC, destination_endpoint=args.DST
    )
    task_data.add_item(
        "/share/godata/file1.txt",  # source
        "/~/example-transfer-script-destination.txt",  # dest
    )

    # define the submission step -- we will use it twice below
    def do_submit(client):
        task_doc = client.submit_transfer(task_data)
        task_id = task_doc["task_id"]
        print(f"submitted transfer, task_id={task_id}")


    # try to submit the task
    # if it fails, catch the error...
    try:
        do_submit(transfer_client)
    except globus_sdk.TransferAPIError as err:
        # if the error is something other than consent_required, reraise it,
        # exiting the script with an error message
        if not err.info.consent_required:
            raise

        # we now know that the error is a ConsentRequired
        # print an explanatory message and do the login flow again
        print(
            "Encountered a ConsentRequired error.\n"
            "You must login a second time to grant consents.\n\n"
        )
        transfer_client = login_and_get_transfer_client(
            scopes=err.info.consent_required.required_scopes
        )

        # finally, try the submission a second time, this time with no error
        # handling
        do_submit(transfer_client)


Best-Effort Proactive Handling of ConsentRequired
-------------------------------------------------

The above example works in most cases, and especially when there is a low cost
to failing and retrying an activity.

However, in some cases, responding to ``ConsentRequired`` errors when the task
is submitted is not acceptable. For example, for scripts used in batch job
systems, the user cannot respond to the error until the job is already
executing. The user would rather handle such issues when submitting their job.

``ConsentRequired`` errors in this case can be avoided on a best-effort basis.
Note, however, that the process for consenting ahead of time is more error
prone and complex.

The example below enhances the previous reactive error handling to try an
``ls`` operation before starting to build the task data. If the ``ls`` fails
with ``ConsentRequired``, the user can be put through the relevant login flow.
And if not, we can relatively safely assume that any errors are not relevant.

.. code-block:: python

    import argparse
    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    parser = argparse.ArgumentParser()
    parser.add_argument("SRC")
    parser.add_argument("DST")
    args = parser.parse_args()

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    # we will need to do the login flow potentially twice, so define it as a
    # function
    #
    # we default to using the Transfer "all" scope, but it is settable here
    # look at the ConsentRequired handler below for how this is used
    def login_and_get_transfer_client(*, scopes=TransferScopes.all):
        # note that 'requested_scopes' can be a single scope or a list
        # this did not matter in previous examples but will be leveraged in
        # this one
        auth_client.oauth2_start_flow(requested_scopes=scopes)
        authorize_url = auth_client.oauth2_get_authorize_url()
        print(f"Please go to this URL and login:\n\n{authorize_url}\n")

        auth_code = input("Please enter the code here: ").strip()
        tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
        transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

        # return the TransferClient object, as the result of doing a login
        return globus_sdk.TransferClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
        )


    # get an initial client to try with, which requires a login flow
    transfer_client = login_and_get_transfer_client()

    # now, try an ls on the source and destination to see if ConsentRequired
    # errors are raised
    consent_required_scopes = []


    def check_for_consent_required(target):
        try:
            transfer_client.operation_ls(target, path="/")
        # catch all errors and discard those other than ConsentRequired
        # e.g. ignore PermissionDenied errors as not relevant
        except globus_sdk.TransferAPIError as err:
            if err.info.consent_required:
                consent_required_scopes.extend(err.info.consent_required.required_scopes)


    check_for_consent_required(args.SRC)
    check_for_consent_required(args.DST)

    # the block above may or may not populate this list
    # but if it does, handle ConsentRequired with a new login
    if consent_required_scopes:
        print(
            "One of your endpoints requires consent in order to be used.\n"
            "You must login a second time to grant consents.\n\n"
        )
        transfer_client = login_and_get_transfer_client(scopes=consent_required_scopes)

    # from this point onwards, the example is exactly the same as the reactive
    # case, including the behavior to retry on ConsentRequiredErrors. This is
    # not obvious, but there are cases in which it is necessary -- for example,
    # if a user consents at the start, but the process of building task_data is
    # slow, they could revoke their consent before the submission step
    #
    # in the common case, a single submission with no retry would suffice

    task_data = globus_sdk.TransferData(
        source_endpoint=args.SRC, destination_endpoint=args.DST
    )
    task_data.add_item(
        "/share/godata/file1.txt",  # source
        "/~/example-transfer-script-destination.txt",  # dest
    )


    def do_submit(client):
        task_doc = client.submit_transfer(task_data)
        task_id = task_doc["task_id"]
        print(f"submitted transfer, task_id={task_id}")


    try:
        do_submit(transfer_client)
    except globus_sdk.TransferAPIError as err:
        if not err.info.consent_required:
            raise
        print(
            "Encountered a ConsentRequired error.\n"
            "You must login a second time to grant consents.\n\n"
        )
        transfer_client = login_and_get_transfer_client(
            scopes=err.info.consent_required.required_scopes
        )
        do_submit(transfer_client)
