from globus_sdk import response


class IterableFlowsResponse(response.IterableResponse):
    """
    An iterable response containing a "flows" array.
    """

    default_iter_key = "flows"


class IterableRunsResponse(response.IterableResponse):
    """
    An iterable response containing a "runs" array.
    """

    default_iter_key = "runs"
