import pytest

import globus_sdk


@pytest.fixture
def make_oauth_token_response(make_response):
    """
    response with conveniently formatted names to help with iteration in tests
    """

    def f(client=None):
        return make_response(
            response_class=globus_sdk.services.auth.response.OAuthTokenResponse,
            json_body={
                "access_token": "access_token_1",
                "expires_in": 3600,
                "id_token": "id_token_value",
                "refresh_token": "refresh_token_1",
                "resource_server": "resource_server_1",
                "scope": "scope1",
                "state": "provided_by_client_to_prevent_replay_attacks",
                "token_type": "bearer",
                "other_tokens": [
                    {
                        "access_token": "access_token_2",
                        "expires_in": 3600,
                        "refresh_token": "refresh_token_2",
                        "resource_server": "resource_server_2",
                        "scope": "scope2 scope2:0 scope2:1",
                        "token_type": "bearer",
                    },
                    {
                        "access_token": "access_token_3",
                        "expires_in": 3600,
                        "refresh_token": "refresh_token_3",
                        "resource_server": "resource_server_3",
                        "scope": "scope3:0 scope3:1",
                        "token_type": "bearer",
                    },
                ],
            },
            client=client,
        )

    return f


@pytest.fixture
def make_oauth_dependent_token_response(make_response):
    """
    response with conveniently formatted names to help with iteration in tests
    """

    def f(client=None):
        return make_response(
            response_class=(
                globus_sdk.services.auth.response.OAuthDependentTokenResponse
            ),
            json_body=[
                {
                    "access_token": "access_token_4",
                    "expires_in": 3600,
                    "refresh_token": "refresh_token_4",
                    "resource_server": "resource_server_4",
                    "scope": "scope4",
                    "token_type": "bearer",
                },
                {
                    "access_token": "access_token_5",
                    "expires_in": 3600,
                    "refresh_token": "refresh_token_5",
                    "resource_server": "resource_server_5",
                    "scope": "scope5",
                    "token_type": "bearer",
                },
            ],
            client=client,
        )

    return f


@pytest.fixture
def oauth_token_response(make_oauth_token_response):
    return make_oauth_token_response()


@pytest.fixture
def oauth_dependent_token_response(make_oauth_dependent_token_response):
    return make_oauth_dependent_token_response()
