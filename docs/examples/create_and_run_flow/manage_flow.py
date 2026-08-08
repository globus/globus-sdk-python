import argparse
import sys

import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def get_flows_client(app: globus_sdk.GlobusApp) -> globus_sdk.FlowsClient:
    return globus_sdk.FlowsClient(
        app=app, app_scopes=[globus_sdk.FlowsClient.scopes.manage_flows]
    )


def create_flow(app: globus_sdk.GlobusApp, args: argparse.Namespace) -> None:
    with get_flows_client(app) as flows_client:
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


def delete_flow(app: globus_sdk.GlobusApp, args: argparse.Namespace) -> None:
    with get_flows_client(app) as flows_client:
        print(flows_client.delete_flow(args.flow_id))


def list_flows(app: globus_sdk.GlobusApp) -> None:
    with get_flows_client(app) as flows_client:
        for flow in flows_client.list_flows(filter_roles="flow_owner"):
            print(f"title: {flow['title']}")
            print(f"id: {flow['id']}")
            print()


def run_flow(app: globus_sdk.GlobusApp, args: argparse.Namespace) -> None:
    with globus_sdk.SpecificFlowClient(args.flow_id, app=app) as flow_client:
        print(flow_client.run_flow({}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["logout", "create", "delete", "list", "run"])
    parser.add_argument("-f", "--flow-id", help="Flow ID for delete and run")
    parser.add_argument("-t", "--title", help="Name for create")
    args = parser.parse_args()

    with globus_sdk.UserApp("manage-flow-example", client_id=CLIENT_ID) as app:
        try:
            if args.action == "logout":
                app.logout(sweep=True)
            elif args.action == "create":
                if args.title is None:
                    parser.error("create requires --title")
                create_flow(app, args)
            elif args.action == "delete":
                if args.flow_id is None:
                    parser.error("delete requires --flow-id")
                delete_flow(app, args)
            elif args.action == "list":
                list_flows(app)
            elif args.action == "run":
                if args.flow_id is None:
                    parser.error("run requires --flow-id")
                run_flow(app, args)
            else:
                raise NotImplementedError()
        except globus_sdk.FlowsAPIError as e:
            print(f"API Error: {e.code} {e.message}")
            print(e.text)
            sys.exit(1)


if __name__ == "__main__":
    main()
