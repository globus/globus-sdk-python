from __future__ import annotations

import enum
import typing as t

from globus_sdk._internal.remarshal import strseq_iter
from globus_sdk._internal.type_definitions import UUIDLike
from globus_sdk._missing import MISSING, MissingType
from globus_sdk._payload import GlobusPayload

T = t.TypeVar("T")


class GroupRole(enum.Enum):
    member = "member"
    manager = "manager"
    admin = "admin"


_GROUP_ROLE_T = t.Union[GroupRole, t.Literal["member", "manager", "admin"]]


class GroupMemberVisibility(enum.Enum):
    members = "members"
    managers = "managers"


_GROUP_MEMBER_VISIBILITY_T = t.Union[
    GroupMemberVisibility, t.Literal["members", "managers"]
]


class GroupVisibility(enum.Enum):
    authenticated = "authenticated"
    private = "private"


_GROUP_VISIBILITY_T = t.Union[GroupVisibility, t.Literal["authenticated", "private"]]


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
    t.Literal[
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


def _typename(obj: t.Any) -> str:
    if isinstance(obj, type) and issubclass(obj, enum.Enum):
        return obj.__name__
    return str(obj)


def _fmt_union(obj: t.Any) -> str:
    return " | ".join(_typename(x) for x in t.get_args(obj))


def _docstring_fixer(cls: type[T]) -> type[T]:
    """
    These type aliases are not always rendered correctly by sphinx autodoc.

    Therefore, we state the types explicitly using a doc modifier, so
    that we can reformat them in a sphinx-friendly way.
    """
    if cls.__doc__ is not None:
        cls.__doc__ = cls.__doc__.format(
            _GROUP_ROLE_T=_fmt_union(_GROUP_ROLE_T),
            _GROUP_MEMBER_VISIBILITY_T=_fmt_union(_GROUP_MEMBER_VISIBILITY_T),
            _GROUP_VISIBILITY_T=_fmt_union(_GROUP_VISIBILITY_T),
            _GROUP_REQUIRED_SIGNUP_FIELDS_T=_fmt_union(_GROUP_REQUIRED_SIGNUP_FIELDS_T),
        )
    return cls


class BatchMembershipActions(GlobusPayload):
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

        :param identity_ids: The identities for whom to accept invites
        """
        self.setdefault("accept", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
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

        :param identity_ids: The identities to add to the group
        :param role: The role for the new group members
        """
        self.setdefault("add", []).extend(
            {"identity_id": identity_id, "role": role}
            for identity_id in strseq_iter(identity_ids)
        )
        return self

    def approve_pending(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Approve a list of identities with pending join requests.

        :param identity_ids: The identities to approve as members of the group
        """
        self.setdefault("approve", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self

    def decline_invites(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Decline an invitation for a given set of identities.

        :param identity_ids: The identities for whom invitations should be declined
        """
        self.setdefault("decline", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
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

        :param identity_ids: The identities to invite to the group
        :param role: The role for the invited group members
        """
        self.setdefault("invite", []).extend(
            {"identity_id": identity_id, "role": role}
            for identity_id in strseq_iter(identity_ids)
        )
        return self

    def join(self, identity_ids: t.Iterable[UUIDLike]) -> BatchMembershipActions:
        """
        Join a group with the given identities.  The identities must be in the
        authenticated users identity set.

        :param identity_ids: The identities to use to join the group
        """
        self.setdefault("join", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self

    def leave(self, identity_ids: t.Iterable[UUIDLike]) -> BatchMembershipActions:
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.

        :param identity_ids: The identities to remove from the group
        """
        self.setdefault("leave", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self

    def reject_join_requests(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Reject identities which have requested to join the group.

        :param identity_ids: The identities to reject from the group
        """
        self.setdefault("reject", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self

    def remove_members(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Remove members from a group.  This must be done as an admin or manager
        of the group.

        :param identity_ids: The identities to remove from the group
        """
        self.setdefault("remove", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self

    def request_join(
        self, identity_ids: t.Iterable[UUIDLike]
    ) -> BatchMembershipActions:
        """
        Request to join a group.

        :param identity_ids: The identities to use to request membership in the group
        """
        self.setdefault("request_join", []).extend(
            {"identity_id": identity_id} for identity_id in strseq_iter(identity_ids)
        )
        return self


@_docstring_fixer
class GroupPolicies(GlobusPayload):
    """
    An object used to represent the policy settings of a group.
    This may be used to set or modify group settings.

    See also:
    `API documentation on setting the policies for the group. \
    <https://groups.api.globus.org/redoc#operation/update_policies_v2_groups__group_id__policies_put>`_

    :param is_high_assurance: Whether the group is high assurance or not
    :param group_visibility: The visibility of the group
    :type group_visibility: {_GROUP_VISIBILITY_T}
    :param group_members_visibility: The visibility of the group members
    :type group_members_visibility: {_GROUP_MEMBER_VISIBILITY_T}
    :param join_requests: Whether the group allows join requests or not
    :param signup_fields: The fields required for signup in the group
    :type signup_fields: typing.Iterable[{_GROUP_REQUIRED_SIGNUP_FIELDS_T}]
    :param authentication_assurance_timeout: The session timeout for high assurance
        group policy enforcement
    """

    def __init__(
        self,
        *,
        is_high_assurance: bool,
        group_visibility: _GROUP_VISIBILITY_T,
        group_members_visibility: _GROUP_MEMBER_VISIBILITY_T,
        join_requests: bool,
        signup_fields: t.Iterable[_GROUP_REQUIRED_SIGNUP_FIELDS_T],
        authentication_assurance_timeout: int | None | MissingType = MISSING,
    ) -> None:
        super().__init__()
        self["is_high_assurance"] = is_high_assurance
        self["group_visibility"] = group_visibility
        self["group_members_visibility"] = group_members_visibility
        self["join_requests"] = join_requests
        self["signup_fields"] = list(signup_fields)
        self["authentication_assurance_timeout"] = authentication_assurance_timeout
