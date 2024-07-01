from __future__ import annotations

import random
import string
import uuid
from unittest.mock import Mock

import pytest

import globus_sdk
from globus_sdk import MISSING, MissingType, OAuthTokenResponse, Scope
from globus_sdk.experimental.consents import ConsentForest
from globus_sdk.experimental.globus_app import ValidatingTokenStorage
from globus_sdk.experimental.globus_app.errors import (
    IdentityMismatchError,
    MissingIdentityError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)
from globus_sdk.experimental.tokenstorage import MemoryTokenStorage
from tests.common import make_consent_forest


def test_validating_token_storage_evaluates_identity_requirements(
    make_token_response,
):
    id_a, id_b = str(uuid.uuid4()), str(uuid.uuid4())
    adapter = ValidatingTokenStorage(MemoryTokenStorage(), {})

    # Seed the adapter with an initial identity.
    assert adapter.identity_id is None
    adapter.store_token_response(make_token_response(identity_id=id_a))
    assert adapter.identity_id == id_a

    # We should be able to store a token with the same identity.
    adapter.store_token_response(make_token_response(identity_id=id_a))

    # We should not be able to store a token with a different identity.
    with pytest.raises(IdentityMismatchError):
        adapter.store_token_response(make_token_response(identity_id=id_b))


def test_validating_token_storage_evaluates_root_scope_requirements(
    make_token_response,
):
    adapter = ValidatingTokenStorage(
        MemoryTokenStorage(), {"rs1": [Scope.deserialize("scope1")]}
    )
    identity_id = str(uuid.uuid4())
    valid_token_response = make_token_response(
        scopes={"rs1": "scope1"}, identity_id=identity_id
    )
    invalid_token_response = make_token_response(
        scopes={"rs1": "scope2"}, identity_id=identity_id
    )

    adapter.store_token_response(valid_token_response)
    with pytest.raises(UnmetScopeRequirementsError):
        adapter.store_token_response(invalid_token_response)

    assert (
        adapter.get_token_data("rs1").access_token
        == valid_token_response.by_resource_server["rs1"]["access_token"]
    )


def test_validating_token_storage_evaluates_dependent_scope_requirements(
    make_token_response,
    consent_client,
):
    adapter = ValidatingTokenStorage(
        MemoryTokenStorage(),
        {"rs1": [Scope.deserialize("scope[subscope]")]},
        consent_client=consent_client,
    )
    token_response = make_token_response(scopes={"rs1": "scope"})

    consent_client.mocked_forest = make_consent_forest("scope[different_subscope]")
    with pytest.raises(UnmetScopeRequirementsError):
        adapter.store_token_response(token_response)

    consent_client.mocked_forest = make_consent_forest("scope[subscope]")
    adapter.store_token_response(token_response)

    assert (
        adapter.get_token_data("rs1").access_token
        == token_response.by_resource_server["rs1"]["access_token"]
    )


def test_validating_token_storage_fails_non_identifiable_responses(
    make_token_response,
):
    adapter = ValidatingTokenStorage(MemoryTokenStorage(), {})
    token_response = make_token_response(identity_id=None)

    with pytest.raises(MissingIdentityError):
        adapter.store_token_response(token_response)


def test_validating_token_storage_loads_identity_info_from_storage(
    make_token_response,
):
    # Create an in memory storage adapter
    storage = MemoryTokenStorage()
    adapter = ValidatingTokenStorage(storage, {})

    # Store an identifiable token response
    identity_id = str(uuid.uuid4())
    token_response = make_token_response(identity_id=identity_id)
    adapter.store_token_response(token_response)

    # Create a net new adapter, pointing at the same storage.
    new_adapter = ValidatingTokenStorage(storage, {})
    # Verify that the new adapter loads the identity info from storage.
    assert new_adapter.identity_id == identity_id


def test_validating_token_storage_raises_error_when_no_token_data():
    adapter = ValidatingTokenStorage(MemoryTokenStorage(), {})

    with pytest.raises(MissingTokenError):
        adapter.get_token_data("rs1")


@pytest.fixture
def make_token_response(make_response):
    def _make_token_response(
        scopes: dict[str, str] | None = None,
        identity_id: str | None | MissingType = MISSING,
    ):
        """
        :param scopes: A dictionary of resource server to scope mappings to fill in
            other tokens.
        :param identity_id: The identity ID to use in the ID token. If None, no ID token
            will be included in the response. If MISSING, the ID token will be generated
            with a random identity ID.
        """
        if scopes is None:
            scopes = {}

        auth_scopes = "openid"
        if "auth.globus.org" in scopes:
            auth_scopes = scopes.pop("auth.globus.org")
            if "openid" not in auth_scopes:
                auth_scopes = f"openid {auth_scopes}"

        data = {
            "access_token": _make_access_token(),
            "expires_in": 172800,
            "other_tokens": [
                {
                    "access_token": _make_access_token(),
                    "expires_in": 172800,
                    "resource_server": resource_server,
                    "scope": scope,
                    "token_type": "Bearer",
                }
                for resource_server, scope in scopes.items()
            ],
            "resource_server": "auth.globus.org",
            "scope": auth_scopes,
            "token_type": "Bearer",
        }

        if identity_id is not None:
            # We'll be mocking out the decode_id_token method, so this doesn't need to
            #   be a real JWT ID token.
            data["id_token"] = _make_id_token()

        response = make_response(response_class=OAuthTokenResponse, json_body=data)

        if identity_id is not None:
            decoded_id_token = _decoded_id_token(identity_id)
            response.decode_id_token = lambda: decoded_id_token

        return response

    return _make_token_response


def _decoded_id_token(
    identity_id: str | MissingType = MISSING,
):
    if identity_id is MISSING:
        identity_id = str(uuid.uuid4())
    identity_provider = str(uuid.uuid4())
    aud = str(uuid.uuid4())

    return {
        "at_hash": "RcNb88Asztn-GnRg_0ojS0sSJs1T8YWeYmVkLp7YhdQ",
        "aud": aud,
        "email": None,
        "exp": 1712945792,
        "iat": 1712772992,
        "identity_provider": identity_provider,
        "identity_provider_display_name": "Globus Auth",
        "identity_set": [
            {
                "email": None,
                "identity_provider": identity_provider,
                "identity_provider_display_name": "Globus Auth",
                "last_authentication": None,
                "name": "Pete Sampras",
                "sub": identity_id,
                "username": "kingoftennis@gmail.com",
            }
        ],
        "iss": "https://auth.globus.org",
        "last_authentication": None,
        "name": "Pete Sampras",
        "preferred_username": "kingoftennis@gmail.com",
        "sub": identity_id,
    }


def _make_access_token():
    vocab = string.ascii_letters + string.digits
    return "".join(random.choices(vocab, k=91))


def _make_id_token():
    return "".join(random.choices(string.ascii_letters, k=1000))


@pytest.fixture
def consent_client() -> MockedConsentClient:
    client = Mock(spec=MockedConsentClient)
    client.mocked_forest = None
    get_consents_response_mock = Mock(spec=globus_sdk.GetConsentsResponse)

    def retrieve_mocked_forest():
        if client.mocked_forest is None:
            raise ValueError("No mocked_forest has been set on the client")
        return client.mocked_forest

    get_consents_response_mock.to_forest.side_effect = retrieve_mocked_forest
    client.get_consents.return_value = get_consents_response_mock
    return client


class MockedConsentClient(globus_sdk.AuthClient):
    mocked_forest: ConsentForest | None
