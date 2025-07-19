import globus_sdk
from globus_sdk.services.auth._common import SupportsJWKMethods

# setup clients
nc = globus_sdk.NativeAppAuthClient("foo_client_id")
cc = globus_sdk.ConfidentialAppAuthClient("foo_client_id", "foo_client_secret")

# check that each one supports the JWK methods
x: SupportsJWKMethods
x = nc
x = cc
