from globus_sdk import IterableResponse


class GetConsentsResponse(IterableResponse):
    """
    Response class specific to the Get Consents API

    Provides iteration on the "consents" array in the response.
    """

    default_iter_key = "consents"
