#!/usr/bin/env python

import argparse
import datetime

import globus_sdk
from globus_sdk.experimental.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
USER_APP = UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID)


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

    client = globus_sdk.TimersClient(app=USER_APP)

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
