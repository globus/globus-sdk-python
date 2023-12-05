import globus_sdk
from globus_sdk.scopes import TransferScopes

CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

# requested_scopes specifies a list of scopes to request
# instead of the defaults, only request access to the Transfer API
auth_client.oauth2_start_flow(requested_scopes=TransferScopes.all)
authorize_url = auth_client.oauth2_get_authorize_url()
print(f"Please go to this URL and login:\n\n{authorize_url}\n")

auth_code = input("Please enter the code here: ").strip()
tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

# construct an AccessTokenAuthorizer and use it to construct the
# TransferClient
transfer_client = globus_sdk.TransferClient(
    authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
)

# Replace these with your own collection UUIDs
source_collection_id = "..."
dest_collection_id = "..."

# create a Transfer task consisting of one or more items
task_data = globus_sdk.TransferData(
    source_endpoint=source_collection_id, destination_endpoint=dest_collection_id
)
task_data.add_item(
    "/share/godata/file1.txt",  # source
    "/~/minimal-example-transfer-script-destination.txt",  # dest
)

# submit, getting back the task ID
task_doc = transfer_client.submit_transfer(task_data)
task_id = task_doc["task_id"]
print(f"submitted transfer, task_id={task_id}")
