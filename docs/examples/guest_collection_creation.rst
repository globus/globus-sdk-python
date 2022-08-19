.. _example_guest_collection_creation:

Guest Collection Creation Script
--------------------------------

The following is a script for a Globus client identity to create a GCSv5 guest
collection on an existing mapped collection that it has a valid mapping for.
The constants defined do not refer to a real GCSv5 installation, or client
identity, so the script cannot be run as is.

This script can be tweaked to use a human user identity instead of a client
by changing the authorizer from a ClientCredentialsAuthorizer to an
AccessTokenAuthorizer or RefreshTokenAuthorizer using a user token.

The script assumes the mapped collection is on a storage gateway using
the POSIX connector. Other connectors may need to have connector specific
policy documents passed to create the user credential.

.. code-block:: python

    import globus_sdk
    from globus_sdk import scopes

    # constants
    endpoint_hostname = "abc.xyz.data.globus.org"
    endpoint_id = "59544bb0-8aa3-4c73-9ce4-06d66887bc89"
    mapped_collection_id = "a1c2f515-254a-48a1-a5de-3ea51d783638"
    storage_gateway_id = "1b949deb-d608-403c-a226-a533892789c6"

    # client credentials
    # This client identity must have the needed permissions to create a guest
    # collection on the mapped collection, and a valid mapping to a local account
    # on the storage gateway that matches the local_username
    # If using user tokens, the user must be the one with the correct permissions
    # and identity mapping.
    client_id = "4de65cd7-4363-4510-b652-f8d15a43a0af"
    client_secret = "*redacted*"
    local_username = "local-username"

    # The scope the client will need, note that primary scope is for the endpoint,
    # but it has a dependency on the mapped collection's data_access scope
    scope = scopes.GCSEndpointScopeBuilder(endpoint_id).make_mutable("manage_collections")
    scope.add_dependency(scopes.GCSCollectionScopeBuilder(mapped_collection_id).data_access)

    # Build a GCSClient to act as the client by using a ClientCredentialsAuthorizor
    confidential_client = globus_sdk.ConfidentialAppAuthClient(
        client_id=client_id, client_secret=client_secret
    )
    authorizer = globus_sdk.ClientCredentialsAuthorizer(confidential_client, scopes=scope)
    client = globus_sdk.GCSClient(endpoint_hostname, authorizer=authorizer)

    # The identity creating the guest collection must have a user credential on
    # the mapped collection.
    # Note that this call is connector specific. Most connectors will require
    # connector specific policies to be passed here, but POSIX does not.
    credential_document = globus_sdk.UserCredentialDocument(
        storage_gateway_id=storage_gateway_id,
        identity_id=client_id,
        username=local_username,
    )
    client.create_user_credential(credential_document)

    # Create the collection
    collection_document = globus_sdk.GuestCollectionDocument(
        public="True",
        collection_base_path="/",
        display_name="guest_collection",
        mapped_collection_id=mapped_collection_id,
    )
    response = client.create_collection(collection_document)
    guest_collection_id = response["id"]
    print(f"guest collection {guest_collection_id} created")
