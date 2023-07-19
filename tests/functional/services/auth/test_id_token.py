import json
import time

import jwt
import pytest

import globus_sdk
from tests.common import register_api_route

OIDC_CONFIG = {
    "issuer": "https://auth.globus.org",
    "authorization_endpoint": "https://auth.globus.org/v2/oauth2/authorize",
    "userinfo_endpoint": "https://auth.globus.org/v2/oauth2/userinfo",
    "token_endpoint": "https://auth.globus.org/v2/oauth2/token",
    "revocation_endpoint": "https://auth.globus.org/v2/oauth2/token/revoke",
    "jwks_uri": "https://auth.globus.org/jwk.json",
    "response_types_supported": ["code", "token", "token id_token", "id_token"],
    "id_token_signing_alg_values_supported": ["RS512"],
    "scopes_supported": ["openid", "email", "profile"],
    "token_endpoint_auth_methods_supported": ["client_secret_basic"],
    "claims_supported": [
        "at_hash",
        "aud",
        "email",
        "exp",
        "name",
        "nonce",
        "preferred_username",
        "iat",
        "iss",
        "sub",
    ],
    "subject_types_supported": ["public"],
}

JWK = {
    "keys": [
        {
            "alg": "RS512",
            "e": "AQAB",
            "kty": "RSA",
            "n": "73l27Yp7WT2c0Ve7EoGJ13AuKzg-GHU7Mpgx0JKa_hO04gAXSVXRadQy7gmdLLtAK8uBVcV0fHGgsBl4J92t-I7hayiJSLbgbX-sZhI_OfegeOLcSNB9poPS9w60XGqR9buYOW2x-KXXitsmyHXNmg_-1u0uqfKHu9pmST8dcjUYXTM5F3oJpQKeJlSH8daMlDks4xb9Y83EEFRv-ppY965-WTm2NW4pwLlbgGTWFvZ6YS6GTb-mfGwGuzStI0lKZ7dOFx9ryYQ4wSoUVHtIrypT-gbuaT90Z2SkwOH-GaEZJkudctBeGpieOsyC7P40UXpwgGNFy3xoWL4vHpnHmQ",  # noqa: E501
            "use": "sig",
        }
    ]
}
JWK_PEM = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(JWK["keys"][0]))

TOKEN_PAYLOAD = {
    "access_token": "auth_access_token",
    "scope": "profile email openid",
    "expires_in": 172800,
    "token_type": "Bearer",
    "resource_server": "auth.globus.org",
    "state": "_default",
    "refresh_token": "auth_refresh_token",
    "other_tokens": [
        {
            "access_token": "transfer_access_token",
            "scope": "urn:globus:auth:scope:transfer.api.globus.org:all",
            "expires_in": 172800,
            "token_type": "Bearer",
            "resource_server": "transfer.api.globus.org",
            "state": "_default",
            "refresh_token": "transfer_refresh",
        }
    ],
    # this is a real ID token
    # and since the JWK is real as well, it should decode correctly
    "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJjOGFhZDQzZS1kMjc0LTExZTUtYmY5OC04YjAyODk2Y2Y3ODIiLCJvcmdhbml6YXRpb24iOiJHbG9idXMiLCJuYW1lIjoiU3RlcGhlbiBSb3NlbiIsInByZWZlcnJlZF91c2VybmFtZSI6InNpcm9zZW4yQGdsb2J1c2lkLm9yZyIsImlkZW50aXR5X3Byb3ZpZGVyIjoiNDExNDM3NDMtZjNjOC00ZDYwLWJiZGItZWVlY2FiYTg1YmQ5IiwiaWRlbnRpdHlfcHJvdmlkZXJfZGlzcGxheV9uYW1lIjoiR2xvYnVzIElEIiwiZW1haWwiOiJzaXJvc2VuQHVjaGljYWdvLmVkdSIsImxhc3RfYXV0aGVudGljYXRpb24iOjE2MjE0ODEwMDYsImlkZW50aXR5X3NldCI6W3sic3ViIjoiYzhhYWQ0M2UtZDI3NC0xMWU1LWJmOTgtOGIwMjg5NmNmNzgyIiwib3JnYW5pemF0aW9uIjoiR2xvYnVzIiwibmFtZSI6IlN0ZXBoZW4gUm9zZW4iLCJ1c2VybmFtZSI6InNpcm9zZW4yQGdsb2J1c2lkLm9yZyIsImlkZW50aXR5X3Byb3ZpZGVyIjoiNDExNDM3NDMtZjNjOC00ZDYwLWJiZGItZWVlY2FiYTg1YmQ5IiwiaWRlbnRpdHlfcHJvdmlkZXJfZGlzcGxheV9uYW1lIjoiR2xvYnVzIElEIiwiZW1haWwiOiJzaXJvc2VuQHVjaGljYWdvLmVkdSIsImxhc3RfYXV0aGVudGljYXRpb24iOjE2MjE0ODEwMDZ9LHsic3ViIjoiYjZlMjI3ZTgtZGI1Mi0xMWU1LWI2ZmYtYzNiMWNjMjU5ZTBkIiwibmFtZSI6bnVsbCwidXNlcm5hbWUiOiJzaXJvc2VuK2JhZGVtYWlsQGdsb2J1cy5vcmciLCJpZGVudGl0eV9wcm92aWRlciI6IjkyN2Q3MjM4LWY5MTctNGViMi05YWNlLWM1MjNmYTliYTM0ZSIsImlkZW50aXR5X3Byb3ZpZGVyX2Rpc3BsYXlfbmFtZSI6Ikdsb2J1cyBTdGFmZiIsImVtYWlsIjoic2lyb3NlbitiYWRlbWFpbEBnbG9idXMub3JnIiwibGFzdF9hdXRoZW50aWNhdGlvbiI6bnVsbH0seyJzdWIiOiJmN2Y4OWQwYS1kYzllLTExZTUtYWRkMC1hM2NiZDFhNTU5YjMiLCJuYW1lIjpudWxsLCJ1c2VybmFtZSI6InNpcm9zZW4rYmFkZW1haWwyQGdsb2J1cy5vcmciLCJpZGVudGl0eV9wcm92aWRlciI6IjkyN2Q3MjM4LWY5MTctNGViMi05YWNlLWM1MjNmYTliYTM0ZSIsImlkZW50aXR5X3Byb3ZpZGVyX2Rpc3BsYXlfbmFtZSI6Ikdsb2J1cyBTdGFmZiIsImVtYWlsIjoic2lyb3NlbitiYWRlbWFpbDJAZ2xvYnVzLm9yZyIsImxhc3RfYXV0aGVudGljYXRpb24iOm51bGx9XSwiaXNzIjoiaHR0cHM6Ly9hdXRoLmdsb2J1cy5vcmciLCJhdWQiOiI3ZmI1OGUwMC04MzlkLTQ0ZTMtODA0Ny0xMGE1MDI2MTJkY2EiLCJleHAiOjE2MjE2NTM4MTEsImlhdCI6MTYyMTQ4MTAxMSwiYXRfaGFzaCI6IjFQdlVhbmNFdUxfc2cxV1BsNWx1TUVGR2tjTDZQaDh1cWdpVUZzejhkZUEifQ.CtfnFtfM32ICo0euHv9GnpVHFL1jWz0NriPTXAv6w08Ylk9JBJtmB3oMKNSO-1TGoWUPFDp9TFFk6N32VyF0hsVDtT5DT3t5oq0qfqbPrZA3R04HARW0xtcK_ejNDHBmj6wysey3EzjT764XTvcGOe63CKQ_RJm97ulVaseIT0Aet7AYo5tQuOiSOQ70xzL7Oax3W6TrWi3FIAA-PIMSrAJKbsG7imGOVkaIObG9a-X5yTOcrB4IG4Wat-pN_QiCiiOw_LDCF-r455PwalmnSGUugMYfsdL2k3UxqwOMLIppHnx5-UVAzj3mygj8eZTp6imjqxNMdakS3vhG8dtxbw",  # noqa: E501
}

# this is the 'exp' value encoded above
FIXED_JWT_EXPIRATION_TIME = 1621653811


@pytest.fixture
def client():
    # this client ID is the audience for the above id_token
    # the client_id must match the audience in order for the decode to work (we pass it
    # as the audience during decoding)
    return globus_sdk.AuthClient(client_id="7fb58e00-839d-44e3-8047-10a502612dca")


@pytest.fixture(autouse=True)
def register_token_response():
    register_api_route(
        "auth", "/v2/oauth2/token", method="POST", body=json.dumps(TOKEN_PAYLOAD)
    )


@pytest.fixture
def token_response(register_token_response, client):
    return client.oauth2_token(
        {
            "grant_type": "authorization_code",
            "code": "foo",
            "redirect_uri": "https://bar.example.org/",
        }
    )


def test_decode_id_token(token_response):
    register_api_route(
        "auth",
        "/.well-known/openid-configuration",
        method="GET",
        body=json.dumps(OIDC_CONFIG),
    )
    register_api_route("auth", "/jwk.json", method="GET", body=json.dumps(JWK))

    decoded = token_response.decode_id_token(jwt_params={"verify_exp": False})
    assert decoded["preferred_username"] == "sirosen2@globusid.org"


def test_decode_id_token_with_saved_oidc_config(token_response):
    register_api_route("auth", "/jwk.json", method="GET", body=json.dumps(JWK))

    decoded = token_response.decode_id_token(
        openid_configuration=OIDC_CONFIG, jwt_params={"verify_exp": False}
    )
    assert decoded["preferred_username"] == "sirosen2@globusid.org"


def test_decode_id_token_with_saved_oidc_config_and_jwk(token_response):
    decoded = token_response.decode_id_token(
        openid_configuration=OIDC_CONFIG,
        jwk=JWK_PEM,
        jwt_params={"verify_exp": False},
    )
    assert decoded["preferred_username"] == "sirosen2@globusid.org"


def test_invalid_decode_id_token_usage(token_response):
    with pytest.raises(globus_sdk.exc.GlobusSDKUsageError):
        token_response.decode_id_token(jwk=JWK_PEM, jwt_params={"verify_exp": False})


def test_decode_id_token_with_leeway(token_response):
    register_api_route(
        "auth",
        "/.well-known/openid-configuration",
        method="GET",
        body=json.dumps(OIDC_CONFIG),
    )
    register_api_route("auth", "/jwk.json", method="GET", body=json.dumps(JWK))

    # do a decode with a leeway parameter set high enough that the ancient
    # expiration time will be tolerated
    expiration_delta = time.time() - FIXED_JWT_EXPIRATION_TIME
    decoded = token_response.decode_id_token(
        jwt_params={"leeway": expiration_delta + 1}
    )
    assert decoded["preferred_username"] == "sirosen2@globusid.org"
