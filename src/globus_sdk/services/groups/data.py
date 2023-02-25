from __future__ import annotations

import enum
import sys
import typing as t

from globus_sdk import utils
from globus_sdk._types import UUIDLike

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


class GroupRole(enum.Enum):
    member = "member"
    manager = "manager"
    admin = "admin"


_GROUP_ROLE_T = t.Union[GroupRole, Literal["member", "manager", "admin"]]


class GroupMemberVisibility(enum.Enum):
    members = "members"
    managers = "managers"


_GROUP_MEMBER_VISIBILITY_T = t.Union[
    GroupMemberVisibility, Literal["members", "managers"]
]


class GroupVisibility(enum.Enum):
    authenticated = "authenticated"
    private = "private"


_GROUP_VISIBILITY_T = t.Union[GroupVisibility, Literal["authenticated", "private"]]


class GroupRequiredSignupFields(enum.Enum):
    institution = "institution"
    current_project_name = "current_project_name"
    address = "address"
    city = "city"
    state = "state"
    country = "country"
    address1 = "address1"
    address2 = "address2"
    zip = "zip"
    phone = "phone"
    department = "department"
    field_of_science = "field_of_science"


_GROUP_REQUIRED_SIGNUP_FIELDS_T = t.Union[
    GroupRequiredSignupFields,
    Literal[
        "institution",
        "current_project_name",
        "address",
        "city",
        "state",
        "country",
        "address1",
        "address2",
        "zip",
        "phone",
        "department",
        "field_of_science",
    ],
]


class BatchMembershipActions(utils.PayloadWrapper):
    """
    An object used to represent a batch action on memberships of a group.
    `Perform actions on group members
    <https://groups.api.globus.org/redoc#operation/group_membership_post_actions_v2_groups__group_id__post>`_.
    """

    def accept_invites(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Accept invites for identities.  The identities must belong to
        the identity set of authenticated user.
        """
        self.setdefault("accept", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def add_members(
        self,
        identity_ids: t.Iterable[UUIDLike],
        *,
        role: _GROUP_ROLE_T = "member",
    ) -> BatchMembershipActions:
        """
        Add a list of identities to a group with the given role.
        """
        self.setdefault("add", []).extend(
            {"identity_id": identity_id, "role": utils.render_enums_for_api(role)}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def approve_pending(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Approve a list of identities with pending join requests.
        """
        self.setdefault("approve", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def decline_invites(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Decline an invitation for a given set of identities.
        """
        self.setdefault("decline", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def invite_members(
        self,
        identity_ids: t.Iterable[UUIDLike],
        *,
        role: _GROUP_ROLE_T = "member",
    ) -> BatchMembershipActions:
        """
        Invite a list of identities to a group with the given role.
        """
        self.setdefault("invite", []).extend(
            {"identity_id": identity_id, "role": utils.render_enums_for_api(role)}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def join(self, identity_ids: t.Iterable[UUIDLike]) -> BatchMembershipActions:
        """
        Join a group with the given identities.  The identities must be in the
        authenticated users identity set.
        """
        self.setdefault("join", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def leave(self, identity_ids: t.Iterable[UUIDLike]) -> BatchMembershipActions:
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.
        """
        self.setdefault("leave", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def reject_join_requests(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Reject a members that have requested to join the group.
        """
        self.setdefault("reject", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def remove_members(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Remove members from a group.  This must be done as an admin or manager
        of the group.
        """
        self.setdefault("remove", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self

    def request_join(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Request to join a group.
        """
        self.setdefault("request_join", []).extend(
            {"identity_id": identity_id}
            for identity_id in utils.safe_strseq_iter(identity_ids)
        )
        return self


class GroupPolicies(utils.PayloadWrapper):
    """
    An object used to represent the policy settings of a group.
    This may be used to set or modify group settings.

    See also:
    `API documentation on setting the policies for the group. \
    <https://groups.api.globus.org/redoc#operation/update_policies_v2_groups__group_id__policies_put>`_
    """

    def __setitem__(self, key: str, value: t.Any) -> None:
        self.data[key] = utils.render_enums_for_api(value)

    def __init__(
        self,
        *,
        is_high_assurance: bool,
        group_visibility: _GROUP_VISIBILITY_T,
        group_members_visibility: _GROUP_MEMBER_VISIBILITY_T,
        join_requests: bool,
        signup_fields: t.Iterable[_GROUP_REQUIRED_SIGNUP_FIELDS_T],
        authentication_assurance_timeout: int | None = None,
    ):
        super().__init__()
        self["is_high_assurance"] = is_high_assurance
        self["group_visibility"] = utils.render_enums_for_api(group_visibility)
        self["group_members_visibility"] = utils.render_enums_for_api(
            group_members_visibility
        )
        self["join_requests"] = join_requests
        self["signup_fields"] = utils.render_enums_for_api(signup_fields)
        if authentication_assurance_timeout is not None:
            self["authentication_assurance_timeout"] = authentication_assurance_timeout
