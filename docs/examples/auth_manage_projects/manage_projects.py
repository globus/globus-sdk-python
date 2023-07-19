#!/usr/bin/env python

import argparse
import os

import globus_sdk
from globus_sdk.tokenstorage import SimpleJSONFileAdapter

MY_FILE_ADAPTER = SimpleJSONFileAdapter(
    os.path.expanduser("~/.sdk-manage-projects.json")
)

SCOPES = [globus_sdk.AuthClient.scopes.manage_projects, "openid", "email"]
RESOURCE_SERVER = globus_sdk.AuthClient.resource_server

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow(*, session_params: dict | None = None):
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=SCOPES)
    # special note!
    # this works because oauth2_get_authorize_url supports session error data
    # as parameters to build the authorization URL
    # you could do this manually with the following supported parameters:
    #   - session_required_identities
    #   - session_required_single_domain
    #   - session_required_policies
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url(**session_params)
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)
    return tokens


def get_tokens():
    if not MY_FILE_ADAPTER.file_exists():
        # do a login flow, getting back initial tokens
        response = do_login_flow()
        # now store the tokens and pull out the correct token
        MY_FILE_ADAPTER.store(response)
        tokens = response.by_resource_server[RESOURCE_SERVER]
    else:
        # otherwise, we already did login; load the tokens from that file
        tokens = MY_FILE_ADAPTER.get_token_data(RESOURCE_SERVER)

    return tokens


def get_auth_client():
    tokens = get_tokens()
    return globus_sdk.AuthClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(tokens["access_token"])
    )


def create_project(args):
    auth_client = get_auth_client()
    userinfo = auth_client.oauth2_userinfo()
    print(
        auth_client.create_project(
            args.name,
            contact_email=userinfo["email"],
            admin_ids=userinfo["sub"],
        )
    )


def delete_project(args):
    auth_client = get_auth_client()
    print(auth_client.delete_project(args.project_id))


def list_projects():
    auth_client = get_auth_client()
    for project in auth_client.get_projects():
        print(f"name: {project['display_name']}")
        print(f"id: {project['id']}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "delete", "list"])
    parser.add_argument("-p", "--project-id", help="Project ID for delete")
    parser.add_argument("-n", "--name", help="Project name for create")
    args = parser.parse_args()

    try:
        execute(parser, args)
    except globus_sdk.GlobusAPIError as err:
        if err.info.authorization_parameters:
            err_params = err.info.authorization_parameters
            session_params = {}
            if err_params.session_required_identities:
                print("session required identities detected")
                session_params[
                    "session_required_identities"
                ] = err_params.session_required_identities
            if err_params.session_required_single_domain:
                print("session required single domain detected")
                session_params[
                    "session_required_single_domain"
                ] = err_params.session_required_single_domain
            if err_params.session_required_policies:
                print("session required policies detected")
                session_params[
                    "session_required_policies"
                ] = err_params.session_required_policies
            print(session_params)
            print(err_params)
            response = do_login_flow(session_params=session_params)
            # now store the tokens
            MY_FILE_ADAPTER.store(response)
            print(
                "Reauthenticated successfully to satisfy "
                "session requirements. Will now try again.\n"
            )

            # try the action again
            execute(parser, args)
        raise


def execute(parser, args):
    if args.action == "create":
        if args.name is None:
            parser.error("create requires --name")
        create_project(args)
    elif args.action == "delete":
        if args.project_id is None:
            parser.error("delete requires --project-id")
        delete_project(args)
    elif args.action == "list":
        list_projects()
    else:
        raise NotImplementedError()


if __name__ == "__main__":
    main()
