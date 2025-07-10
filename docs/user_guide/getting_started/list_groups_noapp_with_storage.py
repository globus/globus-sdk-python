import os

import globus_sdk
from globus_sdk.token_storage import JSONTokenStorage

# this is the tutorial client ID
# replace this string with your ID for production use
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# define a client for interactions with Globus Auth
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

# define token storage where tokens will be stored between runs
token_storage = JSONTokenStorage(
    os.path.expanduser("~/.list-my-globus-groups-tokens.json")
)


# if there is no stored token file, we have not yet logged in
if not token_storage.file_exists():
    # do a login flow, getting back a token response
    auth_client.oauth2_start_flow(
        requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships,
        refresh_tokens=True,
    )
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    token_response = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    # now store the tokens
    token_storage.store_token_response(token_response)

# load the tokens from the storage -- either freshly stored or loaded from disk
token_data = token_storage.get_token_data(globus_sdk.GroupsClient.resource_server)

# construct the RefreshTokenAuthorizer which writes back to storage on refresh
authorizer = globus_sdk.RefreshTokenAuthorizer(
    token_data.refresh_token,
    auth_client,
    access_token=token_data.access_token,
    expires_at=token_data.expires_at_seconds,
    on_refresh=token_storage.store_token_response,
)

# use that authorizer to authorize the activity of the groups client
groups_client = globus_sdk.GroupsClient(authorizer=authorizer)

# call out to the Groups service to get a listing
my_groups = groups_client.get_my_groups()

# print in CSV format
print("ID,Name,Roles")
for group in my_groups:
    roles = "|".join({m["role"] for m in group["my_memberships"]})
    print(",".join([group["id"], f'"{group["name"]}"', roles]))
