from globus_sdk import exc


class TransferAPIError(exc.GlobusAPIError):
    """
    Error class for the Transfer API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides:

    :ivar request_id: Unique identifier for the request, which should be
                      provided when contacting support@globus.org.
    """

    def __init__(self, r):
        self.request_id = None
        super().__init__(r)

    def _get_args(self):
        return (self.http_status, self.code, self.message, self.request_id)

    def _load_from_json(self, data):
        self.code = data["code"]
        self.message = data["message"]
        self.request_id = data["request_id"]
