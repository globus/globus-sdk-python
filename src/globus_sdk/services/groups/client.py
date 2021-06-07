from globus_sdk import client

from .errors import GroupsAPIError


class GroupsClient(client.BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    error_class = GroupsAPIError
    service_name = "groups"
