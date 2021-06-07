import logging

from globus_sdk import exc

log = logging.getLogger(__name__)


class AuthAPIError(exc.GlobusAPIError):
    """
    Error class for the API components of Globus Auth.

    Customizes JSON parsing.
    """

    def _load_from_json(self, data):
        """
        Load error data from a JSON document.

        Looks for a top-level "error" attribute in addition to the other
        standard API error attributes. It's not clear whether or not this
        should be a behavior of the base class.

        Handles the case in which an error does not conform to base-class
        expectations with a `no_extractable_message` message.
        """
        if "errors" in data:
            if len(data["errors"]) != 1:
                log.warning(
                    "Doing JSON load of error response with multiple "
                    "errors. Exception data will only include the "
                    "first error, but there are really %d errors",
                    len(data["errors"]),
                )
            # TODO: handle responses with more than one error
            data = data["errors"][0]

        self.code = data.get("code", "Error")

        if "message" in data:
            self.message = data["message"]
        elif "detail" in data:
            self.message = data["detail"]
        elif "error" in data and isinstance(data["error"], str):
            self.message = data["error"]
        else:
            self.message = "no_extractable_message"
