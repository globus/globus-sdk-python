import globus_sdk
import globus_sdk.gare

# this is the SDK tutorial client ID, replace with your own ID
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
# set the collection ID to your test collection
COLLECTION_ID = "..."


def print_ls_data(client):
    ls_result = client.operation_ls(COLLECTION_ID)
    for item in ls_result:
        name = item["name"]
        if item["type"] == "dir":
            name += "/"
        print(name)


with globus_sdk.UserApp("ls-session", client_id=NATIVE_CLIENT_ID) as app:
    client = globus_sdk.TransferClient(app=app)

    # because the recommended test configuration uses a mapped collection
    # without High Assurance capabilities, it will have a data_access scope
    # requirement
    # comment out this line if your collection does not use data_access
    client.add_app_data_access_scope(COLLECTION_ID)

    # try to run the desired operation (`print_ls_data`)
    try:
        print_ls_data(client)
    # catch the possible API error
    except globus_sdk.TransferAPIError as err:
        # if there are authorization parameters data in the error,
        # use it to redrive login
        if err.info.authorization_parameters:
            print("An authorization requirement was not met. Logging in again...")

            gare = globus_sdk.gare.to_gare(err)
            params = gare.authorization_parameters
            # set 'prompt=login', which guarantees a fresh login without
            # reliance on the browser session
            params.prompt = "login"

            # pass these parameters into a login flow
            app.login(auth_params=params)

            # rerun the desired print_ls_data() operation
            print_ls_data(client)

        # otherwise, there are no authorization parameters, so reraise the error
        else:
            raise
