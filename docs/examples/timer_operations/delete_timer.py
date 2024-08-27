#!/usr/bin/env python

import argparse

import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow():
    # we will want to request a 'timer' scope for managing timers
    scope = globus_sdk.TimersClient.scopes.timer

    # run the login flow, finishing with a token exchange
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=scope)
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)

    # pull out the tokens for Globus Timers from the response
    return tokens.by_resource_server[globus_sdk.TimersClient.resource_server]


def create_timers_client():
    tokens = do_login_flow()
    return globus_sdk.TimersClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(tokens["access_token"])
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("TIMER_ID")
    args = parser.parse_args()

    client = create_timers_client()

    client.delete_timer(args.TIMER_ID)
    print("Finished deleting timer.")


if __name__ == "__main__":
    main()
