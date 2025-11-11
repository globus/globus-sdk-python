import globus_sdk

# this is the tutorial client ID
# replace this string with your ID for production use
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

with globus_sdk.UserApp("my-user-app", client_id=CLIENT_ID) as my_app:
    with globus_sdk.GroupsClient(app=my_app) as groups_client:
        my_groups = groups_client.get_my_groups()

# print in CSV format
print("ID,Name,Roles")
for group in my_groups:
    roles = "|".join({m["role"] for m in group["my_memberships"]})
    print(",".join([group["id"], f'"{group["name"]}"', roles]))
