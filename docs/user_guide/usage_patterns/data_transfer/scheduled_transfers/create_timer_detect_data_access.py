import datetime

import globus_sdk
from globus_sdk.experimental.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# Globus Tutorial Collection 1
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
SRC_PATH = "/home/share/godata/file1.txt"

# Globus Tutorial Collection 2
# https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"
DST_PATH = "/~/example-timer-destination.txt"


def uses_data_access(client: globus_sdk.TransferClient, collection_id: str) -> bool:
    """
    Lookup the given collection ID.
    Having looked up the record, return `True` if it uses a `data_access` scope
    and `False` otherwise.
    """
    doc = client.get_endpoint(collection_id)
    if doc["entity_type"] != "GCSv5_mapped_collection":
        return False
    if doc["high_assurance"]:
        return False
    return True


with UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID) as app:
    # as with an immediate data transfer, we take our input data and wrap them in
    # a TransferData object, representing the transfer task
    transfer_request = globus_sdk.TransferData(SRC_COLLECTION, DST_COLLECTION)
    transfer_request.add_item(SRC_PATH, DST_PATH)

    # we'll define the timer as one which runs every hour for 3 days
    # declare these data in the form of a "schedule" for the timer
    #
    # a wide variety of schedules are possible here; to setup a recurring timer:
    # - you MUST declare an interval for the timer (`interval_seconds`)
    # - you MAY declare an end condition (`end`)
    schedule = globus_sdk.RecurringTimerSchedule(
        interval_seconds=3600,
        end={
            "condition": "time",
            "datetime": datetime.datetime.now() + datetime.timedelta(days=3),
        },
    )

    with (
        # we need a TransferClient, for the needs_data_access helper
        globus_sdk.TransferClient(app=app) as transfer_client,
        # create a TimersClient to interact with the service, and register any
        # data_access scopes for the collections
        globus_sdk.TimersClient(app=app) as timers_client,
    ):
        # Detect on each collection whether or not we need `data_access` scopes and
        # apply if necessary
        if uses_data_access(transfer_client, SRC_COLLECTION):
            timers_client.add_app_transfer_data_access_scope(SRC_COLLECTION)
        if uses_data_access(transfer_client, DST_COLLECTION):
            timers_client.add_app_transfer_data_access_scope(DST_COLLECTION)

        # submit the creation request to the service, printing out the
        # ID of your new timer after it's created -- you can find it in
        # https://app.globus.org/activity/timers
        timer = timers_client.create_timer(
            globus_sdk.TransferTimer(
                name=(
                    "create-timer-example "
                    f"[created at {datetime.datetime.now().isoformat()}]"
                ),
                body=transfer_request,
                schedule=schedule,
            )
        )
    print("Finished submitting timer.")
    print(f"timer_id: {timer['timer']['job_id']}")
