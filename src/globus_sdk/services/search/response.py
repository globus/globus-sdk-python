from globus_sdk.response import IterableResponse


class IndexListResponse(IterableResponse):
    """
    Iterable response class for /v1/index_list
    """

    default_iter_key = "index_list"
