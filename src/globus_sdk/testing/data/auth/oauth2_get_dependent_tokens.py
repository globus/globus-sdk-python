from globus_sdk._testing.models import RegisteredResponse, ResponseSet

RESPONSES = ResponseSet(
    groups=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        json=[
            {
                "scope": "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships",  # noqa: E501
                "access_token": "groupsToken",
                "token_type": "bearer",
                "expires_in": 120,
                "resource_server": "groups.api.globus.org",
            }
        ],
        metadata={
            "rs_data": {
                "groups.api.globus.org": {
                    "access_token": "groupsToken",
                    "scope": "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships",  # noqa: E501
                }
            }
        },
    ),
    groups_with_refresh_token=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        json=[
            {
                "scope": "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships",  # noqa: E501
                "access_token": "groupsToken",
                "refresh_token": "groupsRefreshToken",
                "token_type": "bearer",
                "expires_in": 120,
                "resource_server": "groups.api.globus.org",
            }
        ],
        metadata={
            "rs_data": {
                "groups.api.globus.org": {
                    "access_token": "groupsToken",
                    "refresh_token": "groupsRefreshToken",
                    "scope": "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships",  # noqa: E501
                }
            }
        },
    ),
)
