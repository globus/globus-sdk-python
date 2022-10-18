import typing as t

from globus_sdk import response
from globus_sdk._types import UUIDLike

from .client import GroupsClient
from .data import (
    BatchMembershipActions,
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupRole,
    GroupVisibility,
)


class GroupsManager:
    """
    A wrapper for the groups client with common membership and group actions
    wrapped in convenient methods with parameters and type hints.

    .. automethodlist:: globus_sdk.GroupsManager
    """

    def __init__(self, client: t.Optional[GroupsClient] = None) -> None:
        self.client = client or GroupsClient()

    def create_group(
        self, name: str, description: str, *, parent_id: t.Optional[UUIDLike] = None
    ) -> response.GlobusHTTPResponse:
        """
        Create a group with the given name.  If a parent id is included, the
        group will be a subgroup of the given parent group.
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
        group_visibility: GroupVisibility,
        group_members_visibility: GroupMemberVisibility,
        join_requests: bool,
        signup_fields: t.Iterable[GroupRequiredSignupFields],
        authentication_assurance_timeout: t.Optional[int] = None,
    ) -> response.GlobusHTTPResponse:
        """
        Set the group policies for the given group.
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
        """
        actions = BatchMembershipActions().accept_invites([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def add_member(
        self,
        group_id: UUIDLike,
        identity_id: UUIDLike,
        *,
        role: GroupRole = GroupRole.member,
    ) -> response.GlobusHTTPResponse:
        """
        Add a list of identities to a group with the given role.
        """
        actions = BatchMembershipActions().add_members([identity_id], role=role)
        return self.client.batch_membership_action(group_id, actions)

    def approve_pending(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Approve a list of identities with pending join requests.
        """
        actions = BatchMembershipActions().approve_pending([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def decline_invite(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Decline an invitation for a given identity.
        """
        actions = BatchMembershipActions().decline_invites([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def invite_member(
        self,
        group_id: UUIDLike,
        identity_id: UUIDLike,
        *,
        role: GroupRole = GroupRole.member,
    ) -> response.GlobusHTTPResponse:
        """
        Invite an identity to a group with the given role.
        """
        actions = BatchMembershipActions().invite_members([identity_id], role=role)
        return self.client.batch_membership_action(group_id, actions)

    def join(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Join a group with the given identity.  The identity must be in the
        authenticated users identity set.
        """
        actions = BatchMembershipActions().join([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def leave(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.
        """
        actions = BatchMembershipActions().leave([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def reject_join_request(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Reject a member that has requested to join the group.
        """
        actions = BatchMembershipActions().reject_join_requests([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def remove_member(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Remove members from a group.  This must be done as an admin or manager
        of the group.
        """
        actions = BatchMembershipActions().remove_members([identity_id])
        return self.client.batch_membership_action(group_id, actions)

    def request_join(
        self, group_id: UUIDLike, identity_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        Request to join a group.
        """
        actions = BatchMembershipActions().request_join([identity_id])
        return self.client.batch_membership_action(group_id, actions)
