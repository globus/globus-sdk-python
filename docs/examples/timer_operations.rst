Timer Operations Script
-----------------------

This example demonstrates the usage of methods on the Timer client to
schedule a recurring Transfer task.

.. code-block:: python

    import os
    from datetime import datetime, timedelta

    from globus_sdk import (
        AccessTokenAuthorizer,
        NativeAppAuthClient,
        TimerClient,
        TimerJob,
        TransferData,
    )
    from globus_sdk.scopes import (
        GCSCollectionScopeBuilder,
        MutableScope,
        TimerScopes,
        TransferScopes,
    )

    GOEP1 = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
    GOEP2 = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"
    NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    TIMER_CLIENT_ID = "524230d7-ea86-4a52-8312-86065a9e0417"

    # If any of the collections you're targeting are mapped collections
    # that require data_access scopes, include them in this list
    MAPPED_COLLECTION_IDS = []

    # Build a scope that will give the Timer service
    # access to perform transfers on your behalf
    timer_scope = TimerScopes.make_mutable("timer")
    transfer_scope = TransferScopes.make_mutable("all")
    transfer_action_provider_scope_string = (
        "https://auth.globus.org/scopes/actions.globus.org/transfer/transfer"
    )
    transfer_action_provider_scope = MutableScope(transfer_action_provider_scope_string)

    # If you declared and mapped collections above, add them to the transfer scope
    for id in MAPPED_COLLECTION_IDS:
        gcs_data_access_scope = GCSCollectionScopeBuilder(id).make_mutable(
            "data_access",
            optional=True,
        )
        transfer_scope.add_dependency(gcs_data_access_scope)

    transfer_action_provider_scope.add_dependency(transfer_scope)
    timer_scope.add_dependency(transfer_action_provider_scope)

    print(f"Requesting scopes: {timer_scope}")

    # Initialize your native app auth client
    native_client = NativeAppAuthClient(NATIVE_CLIENT_ID)

    # Get access tokens to use for both Transfer and Timer
    native_client.oauth2_start_flow(requested_scopes=timer_scope)
    authorize_url = native_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Enter the auth code here: ").strip()

    token_response = native_client.oauth2_exchange_code_for_tokens(auth_code)
    timer_token = token_response.by_resource_server[TIMER_CLIENT_ID]["access_token"]

    # Create a `TransferData` object
    data = TransferData(source_endpoint=GOEP1, destination_endpoint=GOEP2)
    data.add_item("/share/godata/file1.txt", "/~/file1.txt")

    # Set up the Timer client
    timer_authorizer = AccessTokenAuthorizer(timer_token)
    timer_client = TimerClient(authorizer=timer_authorizer)

    # Create a Timer job, set to run the above transfer 2 times
    start = datetime.utcnow()
    interval = timedelta(minutes=30)
    name = "sdk-timer-example"
    job = TimerJob.from_transfer_data(
        data,
        start,
        interval,
        stop_after_n=2,
        name=name,
        scope=transfer_action_provider_scope_string,
    )
    response = timer_client.create_job(job)
    assert response.http_status == 201
    job_id = response["job_id"]
    print(f"Timer job ID: {job_id}")

    all_jobs = timer_client.list_jobs()
    assert job_id in {job["job_id"] for job in timer_client.list_jobs()["jobs"]}

    get_job_response = timer_client.get_job(job_id)
    assert get_job_response.http_status == 200
    assert get_job_response["name"] == name

    # Later, you could run this function to clean up the job:
    def delete_timer_job(job_id):
        delete_job_response = timer_client.delete_job(job_id)
        assert delete_job_response.http_status == 200
