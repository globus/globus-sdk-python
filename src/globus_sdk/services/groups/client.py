from globus_sdk.base import BaseClient

from .errors import GroupsAPIError


class GroupsClient(BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    error_class = GroupsAPIError
    service_name = "groups"
