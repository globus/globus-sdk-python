#!/usr/bin/env python

import globus_sdk
from globus_sdk.experimental.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
USER_APP = UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID)


def main():
    client = globus_sdk.TimersClient(app=USER_APP)

    first = True
    for record in client.list_jobs(query_params={"filter_active": True})["jobs"]:
        if not first:
            print("---")
        first = False
        print("name:", record["name"])
        print("id:", record["job_id"])


if __name__ == "__main__":
    main()
