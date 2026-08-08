import argparse
import sys

import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def run_flow(app: globus_sdk.GlobusApp, args: argparse.Namespace) -> None:
    with globus_sdk.SpecificFlowClient(args.FLOW_ID, app=app) as flow_client:
        print(flow_client.run_flow({}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("FLOW_ID", help="Flow ID to run")
    args = parser.parse_args()

    with globus_sdk.UserApp("manage-flow-example", client_id=CLIENT_ID) as app:
        try:
            run_flow(app, args)
        except globus_sdk.FlowsAPIError as e:
            print(f"API Error: {e.code} {e.message}")
            print(e.text)
            sys.exit(1)


if __name__ == "__main__":
    main()
