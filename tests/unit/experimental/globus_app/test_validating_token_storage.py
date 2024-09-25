from __future__ import annotations

import random
import string
import uuid
from unittest.mock import Mock

import pytest

import globus_sdk
from globus_sdk import (
    MISSING,
    MissingType,
    OAuthRefreshTokenResponse,
    OAuthTokenResponse,
    Scope,
)
from globus_sdk.experimental.globus_app import (
    ScopeRequirementsValidator,
    UnchangingIdentityIDValidator,
    ValidatingTokenStorage,
)
from globus_sdk.experimental.globus_app.errors import (
    IdentityMismatchError,
    MissingIdentityError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)
from globus_sdk.scopes.consents import ConsentForest
from globus_sdk.tokenstorage import MemoryTokenStorage
from tests.common import make_consent_forest


def _make_memstorage_with_scope_validator(consent_client, scope_requirements):
    scope_validator = ScopeRequirementsValidator(scope_requirements, consent_client)
    return ValidatingTokenStorage(MemoryTokenStorage(), validators=(scope_validator,))


def _make_memstorage_with_identity_id_validator():
    identity_validator = UnchangingIdentityIDValidator()
    return ValidatingTokenStorage(
        MemoryTokenStorage(), validators=(identity_validator,)
    )


def test_validating_token_storage_passes_calls_through():
    # test that the major methods are called on the inner storage:
    # - get_token_data
    # - get_token_data_by_resource_server
    # - remove_token_data
    mock_storage = Mock()
    mock_storage.get_token_data_by_resource_server.return_value = {}
    instance = ValidatingTokenStorage(mock_storage)

    mock_storage.get_token_data.assert_not_called()
    instance.get_token_data("foo")
    mock_storage.get_token_data.assert_called_once_with("foo")

    mock_storage.remove_token_data.assert_not_called()
    instance.remove_token_data("foo")
    mock_storage.remove_token_data.assert_called_once_with("foo")

    # small subtlety here:
    # get_token_data_by_resource_server gets called once on init
    # so check that after we invoke it, the call count is 2
    mock_storage.get_token_data_by_resource_server.assert_called_once()
    instance.get_token_data_by_resource_server()
    assert len(mock_storage.get_token_data_by_resource_server.mock_calls) == 2


def test_validating_token_storage_defaults_to_no_validators():
    # basic contract test -- there should be no "out of the box" validators
    instance = ValidatingTokenStorage(MemoryTokenStorage())
    assert len(instance.validators) == 0


def test_validating_token_storage_initially_calls_validators_with_null_identity_id(
    make_token_response,
):
    # assuming there's no initial token data in storage, on the initial store call
    # there will be an identity_id in the token data but not in the "prior" data slot
    mock_validator = Mock()
    instance = ValidatingTokenStorage(
        MemoryTokenStorage(), validators=(mock_validator,)
    )

    identity_id = str(uuid.uuid4())
    instance.store_token_response(make_token_response(identity_id=identity_id))

    mock_validator.before_store.assert_called_once()
    call_args = mock_validator.before_store.call_args
    assert len(call_args.kwargs) == 0
    assert len(call_args.args) == 2
    token_data, context = call_args.args
    assert context.prior_identity_id is None
    assert context.token_data_identity_id == identity_id


def test_validators_are_invoked_even_when_retrieving_empty_data():
    # `get_token-data_by_resource_server` will invoke validators, even if there is no
    # data available
    mock_validator = Mock()
    instance = ValidatingTokenStorage(
        MemoryTokenStorage(), validators=(mock_validator,)
    )

    data = instance.get_token_data_by_resource_server()
    assert data == {}
    mock_validator.after_retrieve.assert_called_once()


def test_validating_token_storage_evaluates_identity_requirements(make_token_response):
    id_a, id_b = str(uuid.uuid4()), str(uuid.uuid4())
    adapter = _make_memstorage_with_identity_id_validator()

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
    adapter = _make_memstorage_with_scope_validator(
        consent_client, {"rs1": [Scope.deserialize("scope1")]}
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


def test_storage_with_scope_validator_evaluates_dependent_scope_requirements(
    make_token_response, consent_client
):
    adapter = _make_memstorage_with_scope_validator(
        consent_client, {"rs1": [Scope.deserialize("scope[subscope]")]}
    )
    token_response = make_token_response(scopes={"rs1": "scope"})
    adapter.store_token_response(token_response)

    consent_client.mocked_forest = make_consent_forest("scope[different_subscope]")
    with pytest.raises(UnmetScopeRequirementsError):
        adapter.get_token_data("rs1")

    consent_client.mocked_forest = make_consent_forest("scope[subscope]")
    adapter.store_token_response(token_response)

    assert (
        adapter.get_token_data("rs1").access_token
        == token_response.by_resource_server["rs1"]["access_token"]
    )


def test_validating_token_storage_fails_non_identifiable_responses(
    make_token_response,
):
    adapter = _make_memstorage_with_identity_id_validator()
    token_response = make_token_response(identity_id=None)

    with pytest.raises(MissingIdentityError):
        adapter.store_token_response(token_response)


def test_validating_token_storage_loads_identity_info_from_storage(
    make_token_response,
):
    # Create an in memory storage adapter
    storage = MemoryTokenStorage()
    adapter = ValidatingTokenStorage(storage)

    # Store an identifiable token response
    identity_id = str(uuid.uuid4())
    token_response = make_token_response(identity_id=identity_id)
    adapter.store_token_response(token_response)

    # Create a net new adapter, pointing at the same storage.
    new_adapter = ValidatingTokenStorage(storage)
    # Verify that the new adapter loads the identity info from storage.
    assert new_adapter.identity_id == identity_id


def test_validating_token_storage_stores_with_saved_identity_id_on_refresh_tokens(
    make_token_response,
):
    # Create an in memory storage adapter with identity_id verification
    adapter = _make_memstorage_with_identity_id_validator()

    # Store an identifiable token response
    identity_id = str(uuid.uuid4())
    token_response = make_token_response(identity_id=identity_id)
    adapter.store_token_response(token_response)

    # now get and store a replacement token response, identified with a different user
    # however, in this case make it a refresh token response
    other_identity_id = str(uuid.uuid4())
    refresh_token_response = make_token_response(
        response_class=OAuthRefreshTokenResponse, identity_id=other_identity_id
    )
    adapter.store_token_response(refresh_token_response)

    # read back the data, and verify that it contains tokens from the refresh, but the
    # original identity_id
    result = adapter.get_token_data("auth.globus.org")
    assert result.access_token == refresh_token_response["access_token"]
    assert result.identity_id == identity_id


def test_validating_token_storage_raises_error_when_no_token_data():
    adapter = ValidatingTokenStorage(MemoryTokenStorage())

    with pytest.raises(MissingTokenError):
        adapter.get_token_data("rs1")


@pytest.fixture
def make_token_response(make_response):
    def _make_token_response(
        scopes: dict[str, str] | None = None,
        identity_id: str | None | MissingType = MISSING,
        response_class: type[OAuthTokenResponse] = OAuthTokenResponse,
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

        response = make_response(response_class=response_class, json_body=data)

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
