from __future__ import annotations

import typing as t

from globus_sdk import client, response, utils
from globus_sdk._types import UUIDLike
from globus_sdk.scopes import GroupsScopes, Scope

from .data import BatchMembershipActions, GroupPolicies
from .errors import GroupsAPIError


class GroupsClient(client.BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    .. sdk-sphinx-copy-params:: BaseClient

    This provides a relatively low level client to public groups API endpoints.
    You may also consider looking at the GroupsManager as a simpler interface
    to more common actions.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    # NOTE: setting base_path is no longer considered good practice
    #       see the BaseClient source for details
    base_path = "/v2/"
    error_class = GroupsAPIError
    service_name = "groups"
    scopes = GroupsScopes

    @property
    def default_scope_requirements(self) -> list[Scope]:
        return [Scope(GroupsScopes.view_my_groups_and_memberships)]

    def get_my_groups(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.ArrayResponse:
        """
        Return a list of groups your identity belongs to.

        :param query_params: Additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v2/groups/my_groups``

                .. extdoclink:: Retrieve your groups and membership
                    :service: groups
                    :ref: get_my_groups_and_memberships_v2_groups_my_groups_get
        """
        return response.ArrayResponse(
            self.get("/groups/my_groups", query_params=query_params)
        )

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
        :param include: list of additional fields to include (allowed fields are
            ``memberships``, ``my_memberships``, ``policies``, ``allowed_actions``, and
            ``child_ids``)
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v2/groups/<group_id>``

                .. extdoclink:: Get Group
                    :service: groups
                    :ref: get_group_v2_groups__group_id__get
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            query_params["include"] = ",".join(utils.safe_strseq_iter(include))
        return self.get(f"/groups/{group_id}", query_params=query_params)

    def get_group_by_subscription_id(
        self, subscription_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Using a subscription ID, find the group which provides that subscription.

        :param subscription_id: the subscription ID of the group

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    from globus_sdk import GroupsClient

                    groups = GroupsClient(...)
                    group_id = groups.get_group_by_subscription_id(subscription_id)["group_id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: groups.get_group_by_subscription_id

            .. tab-item:: API Info

                ``GET /v2/subscription_info/<subscription_id>``

                .. extdoclink:: Get Group by Subscription ID
                    :service: groups
                    :ref: get_group_by_subscription_id_v2_subscription_info__subscription_id__get
        """  # noqa: E501
        return self.get(f"/subscription_info/{subscription_id}")

    def delete_group(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Delete a group.

        :param group_id: the ID of the group
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``DELETE /v2/groups/<group_id>``

                .. extdoclink:: Delete a Group
                    :service: groups
                    :ref: delete_group_v2_groups__group_id__delete
        """
        return self.delete(f"/groups/{group_id}", query_params=query_params)

    def create_group(
        self,
        data: dict[str, t.Any],
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Create a group.

        :param data: the group document to create
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``POST /v2/groups``

                .. extdoclink:: Create a Group
                    :service: groups
                    :ref: create_group_v2_groups_post
        """
        return self.post("/groups", data=data, query_params=query_params)

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
        :param data: the group document to use for update
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /v2/groups/<group_id>``

                .. extdoclink:: Update a Group
                    :service: groups
                    :ref: update_group_v2_groups__group_id__put
        """
        return self.put(f"/groups/{group_id}", data=data, query_params=query_params)

    def get_group_policies(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get policies for the given group

        :param group_id: the ID of the group
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v2/groups/<group_id>/policies``

                .. extdoclink:: Get the policies for a group
                    :service: groups
                    :ref: get_policies_v2_groups__group_id__policies_get
        """
        return self.get(f"/groups/{group_id}/policies", query_params=query_params)

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
        :param data: the group policy document to set
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /v2/groups/<group_id>/policies``

                .. extdoclink:: Set the policies for a group
                    :service: groups
                    :ref: update_policies_v2_groups__group_id__policies_put
        """
        return self.put(
            f"/groups/{group_id}/policies", data=data, query_params=query_params
        )

    def get_identity_preferences(
        self, *, query_params: dict[str, t.Any] | None = None
    ) -> response.GlobusHTTPResponse:
        """
        Get identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.

        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v2/preferences``

                .. extdoclink:: Get the preferences for your identity set
                    :service: groups
                    :ref: get_identity_set_preferences_v2_preferences_get
        """
        return self.get("/preferences", query_params=query_params)

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
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    gc = globus_sdk.GroupsClient(...)
                    gc.set_identity_preferences({"allow_add": False})

            .. tab-item:: API Info

                ``PUT /v2/preferences``

                .. extdoclink:: Set the preferences for your identity set
                    :service: groups
                    :ref: put_identity_set_preferences_v2_preferences_put
        """
        return self.put("/preferences", data=data, query_params=query_params)

    def get_membership_fields(
        self,
        group_id: UUIDLike,
        *,
        query_params: dict[str, t.Any] | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Get membership fields for your identities.

        :param group_id: the ID of the group
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``GET /v2/groups/<group_id>/membership_fields``

                .. extdoclink:: Get the membership fields for your identity set
                    :service: groups
                    :ref: get_membership_fields_v2_groups__group_id__membership_fields_get
        """  # noqa: E501
        return self.get(
            f"/groups/{group_id}/membership_fields", query_params=query_params
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
        :param data: the membership fields document
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: API Info

                ``PUT /v2/groups/<group_id>/membership_fields``

                .. extdoclink:: Set the membership fields for your identity set
                    :service: groups
                    :ref: put_membership_fields_v2_groups__group_id__membership_fields_put
        """  # noqa: E501
        return self.put(
            f"/groups/{group_id}/membership_fields",
            data=data,
            query_params=query_params,
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
        :param actions: the batch of membership actions to perform, modifying, creating,
            and removing memberships in the group
        :param query_params: additional passthrough query parameters

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    gc = globus_sdk.GroupsClient(...)
                    group_id = ...
                    batch = globus_sdk.BatchMembershipActions()
                    batch.add_members("ae332d86-d274-11e5-b885-b31714a110e9")
                    batch.invite_members("c699d42e-d274-11e5-bf75-1fc5bf53bb24")
                    gc.batch_membership_action(group_id, batch)

            .. tab-item:: API Info

                ``PUT /v2/groups/<group_id>/membership_fields``

                .. extdoclink:: Perform actions on members of the group
                    :service: groups
                    :ref: group_membership_post_actions_v2_groups__group_id__post
        """
        return self.post(f"/groups/{group_id}", data=actions, query_params=query_params)
