from responses.matchers import query_param_matcher

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

RUN_ID = "cfdaf0a4-0931-40af-b974-b619ce69f401"
OWNER_URN = "urn:globus:auth:identity:944cfbe8-60f8-474d-a634-a0c1ad543a54"
RUN_LOGS_RESPONSE = {
    "limit": 10,
    "has_next_page": False,
    "entries": [
        {
            "time": "2023-04-25T18:54:30.683000+00:00",
            "code": "FlowStarted",
            "description": "The Flow Instance started execution",
            "details": {"input": {}},
        },
        {
            "time": "2023-04-25T18:54:30.715000+00:00",
            "code": "ActionStarted",
            "description": "State SyncHelloWorld of type Action started",
            "details": {
                "state_name": "SyncHelloWorld",
                "state_type": "Action",
                "input": {"echo_string": "sync!"},
            },
        },
        {
            "time": "2023-04-25T18:54:31.850000+00:00",
            "code": "ActionCompleted",
            "description": "State SyncHelloWorld of type Action completed",
            "details": {
                "state_name": "SyncHelloWorld",
                "state_type": "Action",
                "output": {
                    "action_id": "19NqhOnDlt2Y3",
                    "completion_time": "2023-04-25T18:54:31.341170+00:00",
                    "creator_id": OWNER_URN,
                    "details": {"Hello": "World", "hello": "sync!"},
                    "display_status": "SUCCEEDED",
                    "label": None,
                    "manage_by": [],
                    "monitor_by": [],
                    "release_after": None,
                    "start_time": "2023-04-25T18:54:31.340484+00:00",
                    "status": "SUCCEEDED",
                    "state_name": "SyncHelloWorld",
                },
            },
        },
        {
            "time": "2023-04-25T18:54:31.913000+00:00",
            "code": "FlowSucceeded",
            "description": "The Flow Instance completed successfully",
            "details": {
                "output": {
                    "action_id": "19NqhOnDlt2Y3",
                    "completion_time": "2023-04-25T18:54:31.341170+00:00",
                    "creator_id": OWNER_URN,
                    "details": {"Hello": "World", "hello": "sync!"},
                    "display_status": "SUCCEEDED",
                    "label": None,
                    "manage_by": [],
                    "monitor_by": [],
                    "release_after": None,
                    "start_time": "2023-04-25T18:54:31.340484+00:00",
                    "status": "SUCCEEDED",
                    "state_name": "SyncHelloWorld",
                }
            },
        },
    ],
}

PAGINATED_RUN_LOG_RESPONSES = [
    {
        "limit": 10,
        "has_next_page": True,
        "marker": "fake_run_logs_marker",
        "entries": [
            {
                "time": "2023-04-25T18:54:30.683000+00:00",
                "code": "FlowStarted",
                "description": "The Flow Instance started execution",
                "details": {"input": {}},
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassStarted",
                "description": "State PassState of type Pass started",
                "details": {
                    "state_name": "PassState",
                    "state_type": "Pass",
                    "input": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassCompleted",
                "description": "State PassState of type Pass completed",
                "details": {
                    "state_name": "PassState",
                    "state_type": "Pass",
                    "output": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassStarted",
                "description": "State PassState2 of type Pass started",
                "details": {
                    "state_name": "PassState2",
                    "state_type": "Pass",
                    "input": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassCompleted",
                "description": "State PassState2 of type Pass completed",
                "details": {
                    "state_name": "PassState2",
                    "state_type": "Pass",
                    "output": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassStarted",
                "description": "State PassState3 of type Pass started",
                "details": {
                    "state_name": "PassState3",
                    "state_type": "Pass",
                    "input": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassCompleted",
                "description": "State PassState3 of type Pass completed",
                "details": {
                    "state_name": "PassState3",
                    "state_type": "Pass",
                    "output": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassStarted",
                "description": "State PassState4 of type Pass started",
                "details": {
                    "state_name": "PassState4",
                    "state_type": "Pass",
                    "input": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "PassCompleted",
                "description": "State PassState4 of type Pass completed",
                "details": {
                    "state_name": "PassState4",
                    "state_type": "Pass",
                    "output": {},
                },
            },
            {
                "time": "2023-04-25T18:54:30.715000+00:00",
                "code": "ActionStarted",
                "description": "State SyncHelloWorld of type Action started",
                "details": {
                    "state_name": "SyncHelloWorld",
                    "state_type": "Action",
                    "input": {"echo_string": "sync!"},
                },
            },
        ],
    },
    {
        "limit": 10,
        "has_next_page": False,
        "entries": [
            {
                "time": "2023-04-25T18:54:31.850000+00:00",
                "code": "ActionCompleted",
                "description": "State SyncHelloWorld of type Action completed",
                "details": {
                    "state_name": "SyncHelloWorld",
                    "state_type": "Action",
                    "output": {
                        "action_id": "19NqhOnDlt2Y3",
                        "completion_time": "2023-04-25T18:54:31.341170+00:00",
                        "creator_id": OWNER_URN,
                        "details": {"Hello": "World", "hello": "sync!"},
                        "display_status": "SUCCEEDED",
                        "label": None,
                        "manage_by": [],
                        "monitor_by": [],
                        "release_after": None,
                        "start_time": "2023-04-25T18:54:31.340484+00:00",
                        "status": "SUCCEEDED",
                        "state_name": "SyncHelloWorld",
                    },
                },
            },
            {
                "time": "2023-04-25T18:54:31.913000+00:00",
                "code": "FlowSucceeded",
                "description": "The Flow Instance completed successfully",
                "details": {
                    "output": {
                        "action_id": "19NqhOnDlt2Y3",
                        "completion_time": "2023-04-25T18:54:31.341170+00:00",
                        "creator_id": OWNER_URN,
                        "details": {"Hello": "World", "hello": "sync!"},
                        "display_status": "SUCCEEDED",
                        "label": None,
                        "manage_by": [],
                        "monitor_by": [],
                        "release_after": None,
                        "start_time": "2023-04-25T18:54:31.340484+00:00",
                        "status": "SUCCEEDED",
                        "state_name": "SyncHelloWorld",
                    }
                },
            },
        ],
    },
]


RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID},
    default=RegisteredResponse(
        service="flows",
        method="GET",
        path=f"/runs/{RUN_ID}/log",
        json=RUN_LOGS_RESPONSE,
    ),
    paginated=ResponseList(
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}/log",
            json=PAGINATED_RUN_LOG_RESPONSES[0],
            match=[query_param_matcher(params={})],
        ),
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}/log",
            json=PAGINATED_RUN_LOG_RESPONSES[1],
            match=[
                query_param_matcher(
                    params={"marker": PAGINATED_RUN_LOG_RESPONSES[0]["marker"]}
                )
            ],
        ),
    ),
)
