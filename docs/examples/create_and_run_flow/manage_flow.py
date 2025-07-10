#!/usr/bin/env python
import argparse
import os
import sys

import globus_sdk
from globus_sdk.token_storage import SimpleJSONFileAdapter

MY_FILE_ADAPTER = SimpleJSONFileAdapter(os.path.expanduser("~/.sdk-manage-flow.json"))

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow(scope):
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=scope, refresh_tokens=True)
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)
    return tokens


def get_authorizer(flow_id=None):
    if flow_id:
        resource_server = flow_id
        scope = globus_sdk.SpecificFlowClient(flow_id).scopes.user
    else:
        resource_server = globus_sdk.FlowsClient.resource_server
        scope = globus_sdk.FlowsClient.scopes.manage_flows

    # try to load the tokens from the file, possibly returning None
    if MY_FILE_ADAPTER.file_exists():
        tokens = MY_FILE_ADAPTER.get_token_data(resource_server)
    else:
        tokens = None

    if tokens is None:
        # do a login flow, getting back initial tokens
        response = do_login_flow(scope)
        # now store the tokens and pull out the correct token
        MY_FILE_ADAPTER.store(response)
        tokens = response.by_resource_server[resource_server]

    return globus_sdk.RefreshTokenAuthorizer(
        tokens["refresh_token"],
        NATIVE_CLIENT,
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=MY_FILE_ADAPTER.on_refresh,
    )


def get_flows_client():
    return globus_sdk.FlowsClient(authorizer=get_authorizer())


def get_specific_flow_client(flow_id):
    authorizer = get_authorizer(flow_id)
    return globus_sdk.SpecificFlowClient(flow_id, authorizer=authorizer)


def create_flow(args):
    flows_client = get_flows_client()
    print(
        flows_client.create_flow(
            title=args.title,
            definition={
                "StartAt": "DoIt",
                "States": {
                    "DoIt": {
                        "Type": "Action",
                        "ActionUrl": "https://actions.globus.org/hello_world",
                        "Parameters": {
                            "echo_string": "Hello, Asynchronous World!",
                        },
                        "End": True,
                    }
                },
            },
            input_schema={},
            subtitle="A flow created by the SDK tutorial",
        )
    )


def delete_flow(args):
    flows_client = get_flows_client()
    print(flows_client.delete_flow(args.flow_id))


def list_flows():
    flows_client = get_flows_client()
    for flow in flows_client.list_flows(filter_role="flow_owner"):
        print(f"title: {flow['title']}")
        print(f"id: {flow['id']}")
        print()


def run_flow(args):
    flow_client = get_specific_flow_client(args.flow_id)
    print(flow_client.run_flow({}))


def logout():
    for tokendata in MY_FILE_ADAPTER.get_by_resource_server().values():
        for tok_key in ("access_token", "refresh_token"):
            token = tokendata[tok_key]
            NATIVE_CLIENT.oauth2_revoke_token(token)

    os.remove(MY_FILE_ADAPTER.filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["logout", "create", "delete", "list", "run"])
    parser.add_argument("-f", "--flow-id", help="Flow ID for delete and run")
    parser.add_argument("-t", "--title", help="Name for create")
    args = parser.parse_args()

    try:
        if args.action == "logout":
            logout()
        elif args.action == "create":
            if args.title is None:
                parser.error("create requires --title")
            create_flow(args)
        elif args.action == "delete":
            if args.flow_id is None:
                parser.error("delete requires --flow-id")
            delete_flow(args)
        elif args.action == "list":
            list_flows()
        elif args.action == "run":
            if args.flow_id is None:
                parser.error("run requires --flow-id")
            run_flow(args)
        else:
            raise NotImplementedError()
    except globus_sdk.FlowsAPIError as e:
        print(f"API Error: {e.code} {e.message}")
        print(e.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
