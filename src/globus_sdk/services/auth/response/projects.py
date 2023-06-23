from globus_sdk.response import IterableResponse


class GetProjectsResponse(IterableResponse):
    """
    Response class specific to the Get Projects API

    Provides iteration on the "projects" array in the response.
    """

    default_iter_key = "projects"
