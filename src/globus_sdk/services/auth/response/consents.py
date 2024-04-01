from globus_sdk import IterableResponse
from globus_sdk.services.auth.consents import ConsentForest


class GetConsentsResponse(IterableResponse):
    """
    Response class specific to the Get Consents API

    Provides iteration on the "consents" array in the response.
    """

    default_iter_key = "consents"

    def to_forest(self) -> ConsentForest:
        """
        Creates a ConsentForest from the consents in this response.

        ConsentForest is a convenience class to make interacting with the
            tree of consents simpler.
        """
        return ConsentForest(self)
