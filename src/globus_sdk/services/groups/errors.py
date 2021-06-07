from globus_sdk import exc


class GroupsAPIError(exc.GlobusAPIError):
    """Error class for the Globus Groups Service."""
