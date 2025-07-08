from __future__ import annotations

import typing as t

from globus_sdk import response
from globus_sdk._internal.type_definitions import UUIDLike

from .client import GroupsClient
from .data import (
    _GROUP_MEMBER_VISIBILITY_T,
    _GROUP_REQUIRED_SIGNUP_FIELDS_T,
    _GROUP_ROLE_T,
    _GROUP_VISIBILITY_T,
    BatchMembershipActions,
    GroupPolicies,
)


class GroupsManager:
    """
    A wrapper for the groups client with common membership and group actions
    wrapped in convenient methods with parameters and type hints.

    .. automethodlist:: globus_sdk.GroupsManager
    """

    def __init__(self, client: GroupsClient | None = None) -> None:
        self.client = client or GroupsClient()

    def create_group(
        self,
        name: str,
        description: str,
        *,
        parent_id: UUIDLike | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Create a group with the given name.  If a parent ID is included, the
        group will be a subgroup of the given parent group.

        :param name: The name of the group
        :param description: A description of the group
        :param parent_id: The ID of the parent group, if there is one
        """
        data = {
            "name": name,
            "description": description,
            "parent_id": str(parent_id) if parent_id is not None else None,
        }
        return self.client.create_group(data=data)

    def set_group_policies(
        self,
        group_id: UUIDLike,
        *,
        is_high_assurance: bool,
        group_visibility: _GROUP_VISIBILITY_T,
        group_members_visibility: _GROUP_MEMBER_VISIBILITY_T,
        join_requests: bool,
        signup_fields: t.Iterable[_GROUP_REQUIRED_SIGNUP_FIELDS_T],
        authentication_assurance_timeout: int | None = None,
    ) -> response.GlobusHTTPResponse:
        """
        Set the group policies for the given group.

        :param group_id: The ID of the group on which to set policies
        :param is_high_assurance: Whether the group can provide a High Assurance
            guarantee when used for access controls
        :param group_visibility: The visibility of the group
        :param group_members_visibility: The visibility of memberships within the group
        :param join_requests: Whether the group allows users to request to join
        :param signup_fields: The required fields for a user to sign up for the group
        :param authentication_assurance_timeout: The timeout used when this group is
            used to apply a High Assurance authentication guarantee
        """
        data = GroupPolicies(
            is_high_assurance=is_high_assurance,
            group_visibility=group_visibility,
            group_members_visibility=group_members_visibility,
            join_requests=join_requests,
            signup_fields=signup_fields,
            authentication_assurance_timeout=authentication_assurance_timeout,
        )
        return self.client.set_group_policies(group_id, data=data)

    def accept_invite(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Accept invite for an identity.  The identity must belong to
        the identity set of the authenticated user.

        :param group_id: The ID of the group
        :param identity_id: The identity for whom to accept the invite
        """
        actions = BatchMembershipActions().accept_invites([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def add_member(
        self,
        group_id: UUIDLike,
        identity_id: UUIDLike,
        *,
        role: _GROUP_ROLE_T = "member",
    ) -> response.GlobusHTTPResponse:
        """
        Add an identity to a group with the given role.

        :param group_id: The ID of the group
        :param identity_id: The identity to add to the group
        :param role: The role for the new group member
        """
        actions = BatchMembershipActions().add_members([identity_id], role=role)
        return self.client.batch_membership_action(group_id, actions)

    def approve_pending(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Approve an identity with a pending join request.

        :param group_id: The ID of the group
        :param identity_id: The identity to approve as a member of the group
        """
        actions = BatchMembershipActions().approve_pending([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def decline_invite(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Decline an invitation for a given identity.

        :param group_id: The ID of the group
        :param identity_id: The identity for whom to decline the invitation
        """
        actions = BatchMembershipActions().decline_invites([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def invite_member(
        self,
        group_id: UUIDLike,
        identity_id: UUIDLike,
        *,
        role: _GROUP_ROLE_T = "member",
    ) -> response.GlobusHTTPResponse:
        """
        Invite an identity to a group with the given role.

        :param group_id: The ID of the group
        :param identity_id: The identity to invite as a new group member
        :param role: The role for the invited group member
        """
        actions = BatchMembershipActions().invite_members([identity_id], role=role)
        return self.client.batch_membership_action(group_id, actions)

    def join(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Join a group with the given identity.  The identity must be in the
        authenticated users identity set.

        :param group_id: The ID of the group
        :param identity_id: The identity to use to join the group
        """
        actions = BatchMembershipActions().join([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def leave(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.

        :param group_id: The ID of the group
        :param identity_id: The identity to remove from the group
        """
        actions = BatchMembershipActions().leave([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def reject_join_request(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Reject a member that has requested to join the group.

        :param group_id: The ID of the group
        :param identity_id: The identity to reject from the group
        """
        actions = BatchMembershipActions().reject_join_requests([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def remove_member(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Remove a member from a group.  This must be done as an admin or manager
        of the group.

        :param group_id: The ID of the group
        :param identity_id: The identity to remove from the group
        """
        actions = BatchMembershipActions().remove_members([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def request_join(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Request to join a group.

        :param group_id: The ID of the group
        :param identity_id: The identity to use to request membership in the group
        """
        actions = BatchMembershipActions().request_join([identity_id])
        return self.client.batch_membership_action(group_id, actions)
