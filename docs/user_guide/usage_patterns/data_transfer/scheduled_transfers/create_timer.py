import datetime

import globus_sdk
from globus_sdk.experimental.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# Globus Tutorial Collection 1
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
SRC_PATH = "/share/godata/file1.txt"

# Globus Tutorial Collection 2
# https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"
DST_PATH = "/~/example-timer-destination.txt"

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

with UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID) as app:
    # create a TimersClient to interact with the service, and register any data_access
    # scopes for the collections
    with globus_sdk.TimersClient(app=app) as timers_client:
        # Omit this step if the collections are either
        #   (1) A guest collection or (2) high assurance.
        timers_client.add_app_transfer_data_access_scope(
            (SRC_COLLECTION, DST_COLLECTION)
        )

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
