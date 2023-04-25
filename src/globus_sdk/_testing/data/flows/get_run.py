from copy import deepcopy

from responses.matchers import query_param_matcher

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

FLOW_ID = "cc00d0de-bbf3-4cc6-99e1-b21001641282"
RUN_ID = "4e403da9-33ad-49b8-86d1-0ad131a8a475"
USER1 = "urn:globus:auth:identity:1593ddde-c793-40f0-a51d-cd32d2b30d2a"
USER2 = "urn:globus:auth:identity:d50f3ad9-e190-4015-a2d1-6a854069b837"
GROUP = "urn:globus:groups:id:e5dc559a-c8d5-4911-aa77-a3869d99aa99"

FLOW_SCOPE_SUFFIX = f'flow_{FLOW_ID.replace("-", "_")}_user'
FLOW_SCOPE = f"https://auth.globus.org/scopes/{FLOW_ID}/{FLOW_SCOPE_SUFFIX}"
FLOW_DESCRIPTION = {
    "created_at": "2023-04-11T20:00:06.524930+00:00",
    "flow_owner": USER1,
    "created_by": USER1,
    "description": "This flow does some pretty cool stuff",
    "globus_auth_scope": FLOW_SCOPE,
    "id": FLOW_ID,
    "keywords": ["cool"],
    "subtitle": "My Cool Subtitle",
    "title": "My Cool Flow",
    "updated_at": "2023-04-11T20:00:06.524930+00:00",
}
RUN_DETAILS = {
    "code": "FlowSucceeded",
    "description": "The Flow run reached a successful completion state",
    "output": {
        "HelloResult": {
            "action_id": "6RxDm1JOQnG2",
            "completion_time": "2023-04-11T20:01:22.340594+00:00",
            "creator_id": USER1,
            "details": {"Hello": "World", "hello": "foo"},
            "display_status": "SUCCEEDED",
            "label": "My Cool Run",
            "manage_by": [USER2],
            "monitor_by": [GROUP],
            "release_after": None,
            "start_time": "2023-04-11T20:01:19.660251+00:00",
            "state_name": "RunHelloWorld",
            "status": "SUCCEEDED",
        },
        "input": {"echo_string": "foo", "sleep": 2},
    },
}
RUN = {
    "run_id": RUN_ID,
    "action_id": RUN_ID,
    "completion_time": "2023-04-11T20:01:22.917000+00:00",
    "created_by": USER1,
    "details": RUN_DETAILS,
    "display_status": "SUCCEEDED",
    "flow_id": FLOW_ID,
    "flow_last_updated": "2023-04-11T20:00:06.524930+00:00",
    "flow_title": "My Cool Flow",
    "label": "My Cool Run",
    "manage_by": [USER2],
    "monitor_by": [GROUP],
    "run_managers": [USER2],
    "run_monitors": [GROUP],
    "run_owner": USER1,
    "start_time": "2023-04-11T20:01:18.040416+00:00",
    "status": "SUCCEEDED",
    "tags": ["cool", "my"],
    "user_role": "run_owner",
}

RUN_WITH_FLOW_DESCRIPTION = deepcopy(RUN)
RUN_WITH_FLOW_DESCRIPTION["flow_description"] = FLOW_DESCRIPTION

RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID},
    default=ResponseList(
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}",
            json=RUN,
            match=[query_param_matcher(params={"include_flow_description": False})],
        ),
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}",
            json=RUN_WITH_FLOW_DESCRIPTION,
            match=[query_param_matcher(params={"include_flow_description": True})],
        ),
    ),
)
