import globus_sdk
from globus_sdk.experimental.globus_app import UserApp

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
USER_APP = UserApp("my-simple-transfer", client_id=NATIVE_CLIENT_ID)

# Globus Tutorial Collection 1
# https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
ENDPOINT_HOSTNAME = "https://b7a4f1.75bc.data.globus.org"
MAPPED_COLLECTION_ID = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"


def main():
    gcs_client = globus_sdk.GCSClient(ENDPOINT_HOSTNAME, app=USER_APP)

    # Comment out this line if the mapped collection is high assurance
    attach_data_access_scope(gcs_client, MAPPED_COLLECTION_ID)

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


if __name__ == "__main__":
    main()
