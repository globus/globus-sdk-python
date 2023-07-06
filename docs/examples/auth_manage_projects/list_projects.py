#!/usr/bin/env python

import globus_sdk

SCOPES = [globus_sdk.AuthClient.scopes.manage_projects, "openid", "email"]
RESOURCE_SERVER = globus_sdk.AuthClient.resource_server

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow():
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=SCOPES)
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)
    return tokens.by_resource_server[RESOURCE_SERVER]


def get_auth_client():
    tokens = do_login_flow()
    return globus_sdk.AuthClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(tokens["access_token"])
    )


def main():
    auth_client = get_auth_client()
    for project in auth_client.get_projects():
        print(f"name: {project['display_name']}")
        print(f"id: {project['id']}")
        print()


if __name__ == "__main__":
    main()
