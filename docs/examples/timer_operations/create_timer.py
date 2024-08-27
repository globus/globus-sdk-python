#!/usr/bin/env python

import argparse
import datetime

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
    # the source, destination, and path to a file or dir to sync
    parser.add_argument("SOURCE_COLLECTION")
    parser.add_argument("DESTINATION_COLLECTION")
    parser.add_argument("PATH")
    parser.add_argument(
        "--interval-seconds",
        help="How frequently the timer runs, in seconds (default: 1 hour)",
        default=3600,
        type=int,
    )
    parser.add_argument(
        "--days",
        help="How many days to run the timer (default: 2)",
        default=2,
        type=int,
    )
    args = parser.parse_args()

    client = create_timers_client()

    body = globus_sdk.TransferData(
        source_endpoint=args.SOURCE_COLLECTION,
        destination_endpoint=args.DESTINATION_COLLECTION,
    )
    body.add_item(args.PATH, args.PATH)

    # the timer will run until the end date, on whatever interval was requested
    schedule = globus_sdk.RecurringTimerSchedule(
        interval_seconds=args.interval_seconds,
        end={
            "condition": "time",
            "datetime": datetime.datetime.now() + datetime.timedelta(days=args.days),
        },
    )

    timer = client.create_timer(
        timer=globus_sdk.TransferTimer(
            name=(
                "create-timer-example "
                f"[created at {datetime.datetime.now().isoformat()}]"
            ),
            body=body,
            schedule=schedule,
        )
    )
    print("Finished submitting timer.")
    print(f"timer_id: {timer['timer']['job_id']}")


if __name__ == "__main__":
    main()
