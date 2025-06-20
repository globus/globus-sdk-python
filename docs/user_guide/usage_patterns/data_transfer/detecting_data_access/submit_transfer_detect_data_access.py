import globus_sdk


def uses_data_access(
    transfer_client: globus_sdk.TransferClient, collection_id: str
) -> bool:
    """
    Use the provided `transfer_client` to lookup a collection by ID.

    Based on the record, return `True` if it uses a `data_access` scope and `False`
    otherwise.
    """
    doc = transfer_client.get_endpoint(collection_id)
    if doc["entity_type"] != "GCSv5_mapped_collection":
        return False
    if doc["high_assurance"]:
        return False
    return True


# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
USER_APP = globus_sdk.UserApp("detect-data-access-example", client_id=NATIVE_CLIENT_ID)


# Globus Tutorial Collection 1 & 2
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
# https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
# replace with your desired collections
SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"

SRC_PATH = "/home/share/godata/file1.txt"
DST_PATH = "/~/example-transfer-script-destination.txt"

transfer_client = globus_sdk.TransferClient(app=USER_APP)

# check if either source or dest needs data_access, and if so add the relevant
# requirement
if uses_data_access(transfer_client, SRC_COLLECTION):
    transfer_client.add_app_data_access_scope(SRC_COLLECTION)
if uses_data_access(transfer_client, DST_COLLECTION):
    transfer_client.add_app_data_access_scope(DST_COLLECTION)

transfer_request = globus_sdk.TransferData(SRC_COLLECTION, DST_COLLECTION)
transfer_request.add_item(SRC_PATH, DST_PATH)

task = transfer_client.submit_transfer(transfer_request)
print(f"Submitted transfer. Task ID: {task['task_id']}.")
