#!/usr/bin/env python

import argparse
import datetime

import globus_sdk

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def uses_data_access(transfer_client, collection_id):
    doc = transfer_client.get_endpoint(collection_id)
    if doc["entity_type"] != "GCSv5_mapped_collection":
        return False
    if doc["high_assurance"]:
        return False
    return True


def get_data_access_scopes(transfer_client, collection_ids):
    data_access_scopes = []
    for collection_id in collection_ids:
        if uses_data_access(transfer_client, collection_id):
            data_access_scopes.append(
                globus_sdk.GCSClient.get_gcs_collection_scopes(
                    collection_id
                ).data_access
            )
    return data_access_scopes


def do_login_flow(data_access_scopes=None):
    # we will want to request a 'timer' scope for managing timers
    # and a 'transfer:all' scope for inspecting collections
    #
    # if there are data_access scopes to request, we'll need to 'enhance' the Timers
    # scope to be shaped like this:
    #
    #   timers_scope ->
    #     transfer_scope ->
    #       data_access1
    #       data_access2
    #
    # this scope structure encodes permission for Timers to use Transfer on the
    # target collections
    timer_scope = globus_sdk.TimersClient.scopes.timer
    if data_access_scopes:
        transfer_scope = globus_sdk.Scope(globus_sdk.TransferClient.scopes.all)
        for da_scope in data_access_scopes:
            transfer_scope.add_dependency(da_scope)

        timer_scope = globus_sdk.Scope(globus_sdk.TimersClient.scopes.timer)
        timer_scope.add_dependency(transfer_scope)

    scopes = [
        timer_scope,
        globus_sdk.TransferClient.scopes.all,
    ]

    # run the login flow, finishing with a token exchange
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=scopes)
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)

    # return Transfer and Timers tokens
    return tokens.by_resource_server


def create_clients(data_access_scopes=None):
    tokens = do_login_flow(data_access_scopes=data_access_scopes)
    timers_tokens = tokens[globus_sdk.TimersClient.resource_server]
    transfer_tokens = tokens[globus_sdk.TransferClient.resource_server]

    timers_client = globus_sdk.TimersClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(timers_tokens["access_token"])
    )
    transfer_client = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
    )
    return timers_client, transfer_client


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

    # login and get relevant clients, but also check if we need to re-login for
    # data_access and potentially replace the timers_client as a result
    timers_client, transfer_client = create_clients()
    data_access_scopes = get_data_access_scopes(
        transfer_client, [args.SOURCE_COLLECTION, args.DESTINATION_COLLECTION]
    )
    if data_access_scopes:
        timers_client, _ = create_clients(data_access_scopes=data_access_scopes)

    # from this point onwards, the example is the same as the basic create_timer.py
    # script -- we've handled the nuance of data_access

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

    timer = timers_client.create_timer(
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
