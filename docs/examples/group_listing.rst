.. _example_group_listing:

Group Listing Script
--------------------

This example script provides a CSV-formatted listing of the current user's
groups.

It uses the tutorial client ID from the :ref:`tutorials <tutorials>`.
For simplicity, the script will prompt for login on each use.

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import GroupsScopes

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    auth_client.oauth2_start_flow(
        requested_scopes=GroupsScopes.view_my_groups_and_memberships
    )
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    groups_tokens = tokens.by_resource_server["groups.api.globus.org"]

    # construct an AccessTokenAuthorizer and use it to construct the
    # TransferClient
    groups_client = globus_sdk.GroupsClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(groups_tokens["access_token"])
    )

    # print out in CSV format
    # note that 'name' could have a comma in it, so this is slightly unsafe
    print("ID,Name,Type,Session Enforcement,Roles")
    for group in groups_client.get_my_groups():
        # parse the group to get data for output
        if group.get("enforce_session"):
            session_enforcement = "strict"
        else:
            session_enforcement = "not strict"
        roles = ",".join({m["role"] for m in group["my_memberships"]})

        print(
            ",".join(
                [
                    group["id"],
                    group["name"],
                    group["group_type"],
                    session_enforcement,
                    roles,
                ]
            )
        )


.. _example_group_listing_with_token_storage:

Group Listing With Token Storage
--------------------------------

``globus_sdk.token_storage`` provides tools for managing refresh tokens. The
following example script shows how you might use this to provide a complete
script which lists the current user's groups using refresh tokens.


.. code-block:: python

    import os

    from globus_sdk import GroupsClient, NativeAppAuthClient, RefreshTokenAuthorizer
    from globus_sdk.token_storage import SimpleJSONFileAdapter

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    AUTH_CLIENT = NativeAppAuthClient(CLIENT_ID)
    MY_FILE_ADAPTER = SimpleJSONFileAdapter(
        os.path.expanduser("~/.list-my-globus-groups-tokens.json")
    )


    def do_login_flow():
        AUTH_CLIENT.oauth2_start_flow(
            requested_scopes=GroupsClient.scopes.view_my_groups_and_memberships,
            refresh_tokens=True,
        )
        authorize_url = AUTH_CLIENT.oauth2_get_authorize_url()
        print(f"Please go to this URL and login:\n\n{authorize_url}\n")
        auth_code = input("Please enter the code here: ").strip()
        tokens = AUTH_CLIENT.oauth2_exchange_code_for_tokens(auth_code)
        return tokens


    if not MY_FILE_ADAPTER.file_exists():
        # do a login flow, getting back initial tokens
        response = do_login_flow()
        # now store the tokens and pull out the Groups tokens
        MY_FILE_ADAPTER.store(response)
        tokens = response.by_resource_server[GroupsClient.resource_server]
    else:
        # otherwise, we already did login; load the tokens from that file
        tokens = MY_FILE_ADAPTER.get_token_data(GroupsClient.resource_server)

    # construct the RefreshTokenAuthorizer which writes back to storage on refresh
    authorizer = RefreshTokenAuthorizer(
        tokens["refresh_token"],
        AUTH_CLIENT,
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=MY_FILE_ADAPTER.on_refresh,
    )
    # use that authorizer to authorize the activity of the groups client
    groups_client = GroupsClient(authorizer=authorizer)

    # print out in CSV format
    # note that 'name' could have a comma in it, so this is slightly unsafe
    print("ID,Name,Type,Session Enforcement,Roles")
    for group in groups_client.get_my_groups():
        # parse the group to get data for output
        if group.get("enforce_session"):
            session_enforcement = "strict"
        else:
            session_enforcement = "not strict"
        roles = ",".join({m["role"] for m in group["my_memberships"]})

        print(
            ",".join(
                [
                    group["id"],
                    group["name"],
                    group["group_type"],
                    session_enforcement,
                    roles,
                ]
            )
        )
