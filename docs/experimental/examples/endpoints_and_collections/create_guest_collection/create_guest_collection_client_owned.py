import globus_sdk
from globus_sdk.experimental.globus_app import ClientApp

# Confidential Client ID/Secret - <replace these with real client values>
CONFIDENTIAL_CLIENT_ID = "..."
CONFIDENTIAL_CLIENT_SECRET = "..."
CLIENT_APP = ClientApp(
    "my-simple-client-collection",
    client_id=CONFIDENTIAL_CLIENT_ID,
    client_secret=CONFIDENTIAL_CLIENT_SECRET,
)


# Globus Tutorial Collection 1
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
ENDPOINT_HOSTNAME = "https://b7a4f1.75bc.data.globus.org"
STORAGE_GATEWAY_ID = "947460f6-3fcd-4acc-9683-d71e14e5ace1"
MAPPED_COLLECTION_ID = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"


def main():
    gcs_client = globus_sdk.GCSClient(ENDPOINT_HOSTNAME, app=CLIENT_APP)

    # Comment out this line if the mapped collection is high assurance
    attach_data_access_scope(gcs_client, MAPPED_COLLECTION_ID)

    ensure_user_credential(gcs_client)

    collection_request = globus_sdk.GuestCollectionDocument(
        public=True,
        collection_base_path="/",
        display_name="example_guest_collection",
        mapped_collection_id=MAPPED_COLLECTION_ID,
    )

    collection = gcs_client.create_collection(collection_request)
    print(f"Created guest collection. Collection ID: {collection['id']}")


def attach_data_access_scope(gcs_client, collection_id):
    """Compose and attach a ``data_access`` scope for the supplied collection"""
    endpoint_scopes = gcs_client.get_gcs_endpoint_scopes(gcs_client.endpoint_client_id)
    collection_scopes = gcs_client.get_gcs_collection_scopes(collection_id)

    manage_collections = globus_sdk.Scope(endpoint_scopes.manage_collections)
    data_access = globus_sdk.Scope(collection_scopes.data_access, optional=True)

    manage_collections.add_dependency(data_access)

    gcs_client.add_app_scope(manage_collections)


def ensure_user_credential(gcs_client):
    """
    Ensure that the client has a user credential on the client.
    This is the mapping between Globus Auth (OAuth2) and the local system's permissions.
    """
    # Depending on the endpoint & storage gateway, this request document may need to
    # include more complex information such as a local username.
    # Consult with the endpoint owner for more detailed info on user mappings and
    # other specific requirements.
    req = globus_sdk.UserCredentialDocument(storage_gateway_id=STORAGE_GATEWAY_ID)
    try:
        gcs_client.create_user_credential(req)
    except globus_sdk.GCSAPIError as err:
        # A user credential already exists, no need to create it.
        if err.http_status != 409:
            raise


if __name__ == "__main__":
    main()
