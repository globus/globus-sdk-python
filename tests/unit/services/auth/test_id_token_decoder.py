import json
import uuid
from unittest import mock

import pytest
import requests

import globus_sdk


class MockDecoder(globus_sdk.IDTokenDecoder):
    def get_openid_configuration(self):
        return {
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

    def get_jwk(self):
        return mock.Mock()


def test_decoding_defaults_to_client_id_as_audience(mock_client_factory):
    client = mock_client_factory()
    client.client_id = str(uuid.uuid1())

    decoder = MockDecoder(client)

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("")
        assert mock_jwt_decode.call_args.kwargs["audience"] == client.client_id


@pytest.mark.parametrize("audience_value", (None, "myaud"))
def test_decoding_passes_audience(audience_value):
    class MyDecoder(MockDecoder):
        def get_jwt_audience(self):
            return audience_value

    decoder = MyDecoder(mock.Mock())

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("")
        assert mock_jwt_decode.call_args.kwargs["audience"] == audience_value


def test_setting_oidc_config_on_default_decoder_unpacks_data(mock_client_factory):
    oidc_config = {"x": 1}
    raw_response = mock.Mock(spec=requests.Response)
    raw_response.json.return_value = oidc_config
    raw_response.content = json.dumps(oidc_config).encode()
    response = globus_sdk.GlobusHTTPResponse(raw_response, client=mock_client_factory())

    decoder = globus_sdk.IDTokenDecoder(mock.Mock())
    decoder.store_openid_configuration(response)

    assert decoder.get_openid_configuration() == oidc_config


def test_default_jwt_leeway_can_be_overridden_on_instance():
    decoder = MockDecoder(mock.Mock())
    default_leeway = decoder.jwt_leeway
    decoder.jwt_leeway = int(default_leeway * 2)

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("")
        assert mock_jwt_decode.call_args.kwargs["leeway"] == int(default_leeway * 2)
