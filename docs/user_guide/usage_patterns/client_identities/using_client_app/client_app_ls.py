import globus_sdk

# your client credentials
CLIENT_ID = "YOUR ID HERE"
CLIENT_SECRET = "YOUR SECRET HERE"

# the ID of "tutorial collection 1"
TUTORIAL_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"

# create a ClientApp named "app"
with globus_sdk.ClientApp(
    "sample-app",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    config=globus_sdk.GlobusAppConfig(token_storage="memory"),
) as app:
    # create a TransferClient named "tc", bound to "app"
    with globus_sdk.TransferClient(app=app) as tc:

        # because the tutorial collection is of a type which uses a `data_access`
        # scope for fine grained access control, the `data_access` requirement needs
        # to be registered with the app
        tc.add_app_data_access_scope(TUTORIAL_COLLECTION)

        # iterate over the listing results, printing each filename
        for entry in tc.operation_ls(TUTORIAL_COLLECTION, path="/home/share/godata"):
            print(entry["name"])
