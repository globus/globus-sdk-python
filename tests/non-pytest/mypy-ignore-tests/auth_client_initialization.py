import globus_sdk

# ok usage
ac = globus_sdk.AuthClient()
nc = globus_sdk.NativeAppAuthClient("foo_client_id")
cc = globus_sdk.ConfidentialAppAuthClient("foo_client_id", "foo_client_secret")

# base class allows authorizer
authorizer = globus_sdk.AccessTokenAuthorizer("dummytoken")
ac = globus_sdk.AuthClient(authorizer=authorizer)

# subclasses forbid authorizers
nc = globus_sdk.NativeAppAuthClient(  # type: ignore[call-arg]
    "foo_client_id", authorizer=authorizer
)
cc = globus_sdk.ConfidentialAppAuthClient(  # type: ignore[call-arg]
    "foo_client_id", "foo_client_secret", authorizer=authorizer
)
