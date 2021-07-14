from globus_sdk import exc


class TransferAPIError(exc.GlobusAPIError):
    """
    Error class for the Transfer API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides ``request_id``.

    :ivar request_id: Unique identifier for the request, which should be
                      provided when contacting support@globus.org.
    """

    def __init__(self, r):
        self.request_id = None
        super().__init__(r)

    def _get_args(self):
        args = super()._get_args()
        args.append(self.request_id)
        return args

    def _load_from_json(self, data):
        super()._load_from_json(data)
        self.request_id = data.get("request_id")
