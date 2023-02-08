from __future__ import annotations

import typing as t

from globus_sdk import client, response, utils
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import GroupsScopes

from .data import BatchMembershipActions, GroupPolicies
from .errors import GroupsAPIError

C = t.TypeVar("C", bound=t.Callable[..., t.Any])


def _groupdoc(message: str, link: str) -> t.Callable[[C], C]:
    # do not use functools.partial because it doesn't preserve type information
    # see: https://github.com/python/mypy/issues/1484
    def partial(func: C) -> C:
        return utils.doc_api_method(
            message,
            link,
            external_base_url="https://groups.api.globus.org/redoc#operation",
        )(func)

    return partial


class GroupsClient(client.BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    This provides a relatively low level client to public groups API endpoints.
    You may also consider looking at the GroupsManager as a simpler interface
    to more common actions.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    base_path = "/v2/"
    error_class = GroupsAPIError
    service_name = "groups"
    scopes = GroupsScopes

    @_groupdoc(
        "Retrieve your groups and membership",
        "get_my_groups_and_memberships_v2_groups_my_groups_get",
    )
    def get_my_groups(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.ArrayResponse:
        """
        Return a list of groups your identity belongs to.

        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        return response.ArrayResponse(
            self.get("/groups/my_groups", query_params=query_params)
        )

    @_groupdoc("Get Group", "get_group_v2_groups__group_id__get")
    def get_group(
        self,
        group_id: UUIDLike,
        *,
        include: None | str | t.Iterable[str] = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get details about a specific group

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param include: list of additional fields to include (allowed fields are
            ``memberships``, ``my_memberships``, ``policies``, ``allowed_actions``, and
            ``child_ids``)
        :type include: str or iterable of str, optional
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        return self.get(f"/groups/{group_id}", query_params=query_params)

    @_groupdoc("Delete a group", "delete_group_v2_groups__group_id__delete")
    def delete_group(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a group.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.delete(f"/groups/{group_id}", query_params=query_params)

    @_groupdoc("Create a group", "create_group_v2_groups_post")
    def create_group(
        self,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Create a group.

        :param data: the group document to create
        :type data: dict
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.post("/groups", data=data, query_params=query_params)

    @_groupdoc("Update a group", "update_group_v2_groups__group_id__put")
    def update_group(
        self,
        group_id: UUIDLike,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Update a given group.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param data: the group document to use for update
        :type data: dict
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.put(f"/groups/{group_id}", data=data, query_params=query_params)

    @_groupdoc(
        "Get the policies for the group",
        "get_policies_v2_groups__group_id__policies_get",
    )
    def get_group_policies(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get policies for the given group

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.get(f"/groups/{group_id}/policies", query_params=query_params)

    @_groupdoc(
        "Set the policies for the group",
        "update_policies_v2_groups__group_id__policies_put",
    )
    def set_group_policies(
        self,
        group_id: UUIDLike,
        data: dict[str, t.Any] | GroupPolicies,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Set policies for the group.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param data: the group policy document to set
        :type data: dict or ``GroupPolicies``
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.put(
            f"/groups/{group_id}/policies", data=data, query_params=query_params
        )

    @_groupdoc(
        "Get the preferences for your identity set",
        "get_identity_set_preferences_v2_preferences_get",
    )
    def get_identity_preferences(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.GlobusHTTPResponse:
        """
        Get identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.

        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.get("/preferences", query_params=query_params)

    @_groupdoc(
        "Set the preferences for your identity set",
        "put_identity_set_preferences_v2_preferences_put",
    )
    def set_identity_preferences(
        self,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Set identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.

        :param data: the identity set preferences document
        :type data: dict
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional

        **Examples**

        >>> gc = globus_sdk.GroupsClient(...)
        >>> gc.set_identity_preferences({"allow_add": False})
        """
        return self.put("/preferences", data=data, query_params=query_params)

    @_groupdoc(
        "Get the membership fields for your identity set",
        "get_membership_fields_v2_groups__group_id__membership_fields_get",
    )
    def get_membership_fields(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get membership fields for your identities.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.get(
            f"/groups/{group_id}/membership_fields", query_params=query_params
        )

    @_groupdoc(
        "Set the membership fields for your identity set",
        "put_membership_fields_v2_groups__group_id__membership_fields_put",
    )
    def set_membership_fields(
        self,
        group_id: UUIDLike,
        data: dict[t.Any, str],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Set membership fields for your identities.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param data: the membership fields document
        :type data: dict
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional
        """
        return self.put(
            f"/groups/{group_id}/membership_fields",
            data=data,
            query_params=query_params,
        )

    @_groupdoc(
        "Perform actions on members of the group",
        "group_membership_post_actions_v2_groups__group_id__post",
    )
    def batch_membership_action(
        self,
        group_id: UUIDLike,
        actions: dict[str, t.Any] | BatchMembershipActions,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Execute a batch of actions against several group memberships.

        :param group_id: the ID of the group
        :type group_id: str or UUID
        :param actions: the batch of membership actions to perform, modifying, creating,
            and removing memberships in the group
        :type actions: dict or BatchMembershipActions
        :param query_params: additional passthrough query parameters
        :type query_params: dict, optional

        **Examples**

        >>> gc = globus_sdk.GroupsClient(...)
        >>> group_id = ...
        >>> batch = globus_sdk.BatchMembershipActions()
        >>> batch.add_members("ae332d86-d274-11e5-b885-b31714a110e9")
        >>> batch.invite_members("c699d42e-d274-11e5-bf75-1fc5bf53bb24")
        >>> gc.batch_membership_action(group_id, batch)
        """
        return self.post(f"/groups/{group_id}", data=actions, query_params=query_params)
