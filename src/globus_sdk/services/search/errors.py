from globus_sdk import exc


class SearchAPIError(exc.GlobusAPIError):
    """
    Error class for the Search API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides:

    :ivar error_data: Additional object returned in the error response. May be
                      a dict, list, or None.
    """

    def __init__(self, r):
        self.error_data = None
        super().__init__(r)

    def _get_args(self):
        return (self.http_status, self.code, self.message)

    def _load_from_json(self, data):
        self.code = data["code"]
        self.message = data["message"]
        self.error_data = data.get("error_data")
