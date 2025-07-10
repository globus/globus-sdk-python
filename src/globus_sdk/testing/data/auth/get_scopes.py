import uuid

from responses.matchers import query_param_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

SCOPE1 = {
    "scope_string": "https://auth.globus.org/scopes/3f33d83f-ec0a-4190-887d-0622e7c4ee9a/manage",  # noqa: E501
    "allows_refresh_token": False,
    "id": str(uuid.uuid1()),
    "advertised": False,
    "required_domains": [],
    "name": "Client manage scope",
    "description": "Manage configuration of this client",
    "client": "3f33d83f-ec0a-4190-887d-0622e7c4ee9a",
    "dependent_scopes": [],
}

SCOPE2 = {
    "scope_string": "https://auth.globus.org/scopes/dfc9a6d3-3373-4a6d-b0a1-b7026d1559d6/view",  # noqa: E501
    "allows_refresh_token": False,
    "id": str(uuid.uuid1()),
    "advertised": False,
    "required_domains": [],
    "name": "Client view scope",
    "description": "View configuration of this client",
    "client": "dfc9a6d3-3373-4a6d-b0a1-b7026d1559d6",
    "dependent_scopes": [],
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/api/scopes",
        json={"scopes": [SCOPE1, SCOPE2]},
        metadata={
            "scope_ids": [SCOPE1["id"], SCOPE2["id"]],
        },
    ),
    id=RegisteredResponse(
        service="auth",
        path="/v2/api/scopes",
        json={"scopes": [SCOPE1]},
        match=[query_param_matcher(params={"ids": SCOPE1["id"]})],
        metadata={
            "scope_id": SCOPE1["id"],
        },
    ),
    string=RegisteredResponse(
        service="auth",
        path="/v2/api/scopes",
        json={"scopes": [SCOPE2]},
        match=[query_param_matcher(params={"scope_strings": SCOPE2["scope_string"]})],
        metadata={
            "scope_string": SCOPE2["scope_string"],
        },
    ),
)
