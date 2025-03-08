import globus_sdk

# this is the tutorial client ID
# replace this string with your ID for production use
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# create your app
my_app = globus_sdk.UserApp("my-user-app", client_id=CLIENT_ID)

# create a client with your app
groups_client = globus_sdk.GroupsClient(app=my_app)

# print in CSV format
# ('name' could actually have commas in it, so it is quoted)
print("ID,Name,Roles")
for group in groups_client.get_my_groups():
    roles = "|".join({m["role"] for m in group["my_memberships"]})
    print(",".join([group["id"], f'"{group["name"]}"', roles]))
