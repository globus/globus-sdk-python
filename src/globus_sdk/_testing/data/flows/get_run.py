from copy import deepcopy

from responses.matchers import query_param_matcher

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

from ._common import FLOW_DESCRIPTION, RUN, RUN_ID

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
            match=[query_param_matcher(params={})],
        ),
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}",
            json=RUN,
            match=[query_param_matcher(params={"include_flow_description": "False"})],
        ),
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}",
            json=RUN_WITH_FLOW_DESCRIPTION,
            match=[query_param_matcher(params={"include_flow_description": "True"})],
        ),
    ),
)
