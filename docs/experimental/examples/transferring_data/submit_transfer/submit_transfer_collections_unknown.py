import globus_sdk
from globus_sdk.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
USER_APP = UserApp("my-simple-transfer", client_id=NATIVE_CLIENT_ID)

# Globus Tutorial Collection 1
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
SRC_PATH = "/share/godata/file1.txt"

# Globus Tutorial Collection 2
# https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"
DST_PATH = "/~/example-transfer-script-destination.txt"


def main():
    transfer_client = globus_sdk.TransferClient(app=USER_APP)

    transfer_request = globus_sdk.TransferData(
        source_endpoint=SRC_COLLECTION,
        destination_endpoint=DST_COLLECTION,
    )
    transfer_request.add_item(SRC_PATH, DST_PATH)

    try:
        task = transfer_client.submit_transfer(transfer_request)
    except globus_sdk.TransferAPIError as err:
        if not err.info.consent_required:
            raise

        print("Additional consent required.")
        transfer_client.add_app_scope(err.info.consent_required.required_scopes)

        task = transfer_client.submit_transfer(transfer_request)
    print(f"Submitted transfer. Task ID: {task['task_id']}.")


if __name__ == "__main__":
    main()
