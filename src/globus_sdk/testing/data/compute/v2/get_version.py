from responses.matchers import query_param_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

API_VERSION = "1.23.0"
ALL_RESPONSE_DOC = {
    "api": API_VERSION,
    "min_sdk_version": "1.0.0a6",
    "min_endpoint_version": "1.0.0a0",
    "git_sha": "80b2ef87bc546b3b386cf2e1d372f4be50f10bc4",
}

RESPONSES = ResponseSet(
    metadata={"api_version": API_VERSION},
    default=RegisteredResponse(
        service="compute",
        path="/v2/version",
        method="GET",
        json=API_VERSION,  # type: ignore[arg-type]
    ),
    all=RegisteredResponse(
        service="compute",
        path="/v2/version",
        method="GET",
        json=ALL_RESPONSE_DOC,
        match=[query_param_matcher(params={"service": "all"})],
    ),
)
