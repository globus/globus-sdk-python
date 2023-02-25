from globus_sdk import (
    BatchMembershipActions,
    GroupMemberVisibility,
    GroupPolicies,
    GroupRole,
    GroupVisibility,
)

act = BatchMembershipActions()

act.add_members(["foo"], role=GroupRole.member)
act.add_members(["foo"], role=GroupRole.manager)
act.add_members(["foo"], role=GroupRole.admin)
act.add_members(["foo"], role="member")
act.add_members(["foo"], role="manager")
act.add_members(["foo"], role="admin")
act.add_members(["foo"], role="unknown")  # type: ignore[arg-type]

GroupPolicies(
    is_high_assurance=False,
    group_members_visibility="members",
    join_requests=True,
    signup_fields=[],
    group_visibility=GroupVisibility.authenticated,
)
GroupPolicies(
    is_high_assurance=False,
    group_members_visibility="members",
    join_requests=True,
    signup_fields=[],
    group_visibility=GroupVisibility.private,
)
GroupPolicies(
    is_high_assurance=False,
    group_members_visibility="members",
    join_requests=True,
    signup_fields=[],
    group_visibility="authenticated",
)
GroupPolicies(
    is_high_assurance=False,
    group_members_visibility="members",
    join_requests=True,
    signup_fields=[],
    group_visibility="private",
)
GroupPolicies(
    is_high_assurance=False,
    group_members_visibility="members",
    join_requests=True,
    signup_fields=[],
    group_visibility="unknown",  # type: ignore[arg-type]
)

GroupPolicies(
    is_high_assurance=False,
    group_visibility="private",
    join_requests=True,
    signup_fields=[],
    group_members_visibility=GroupMemberVisibility.members,
)
GroupPolicies(
    is_high_assurance=False,
    group_visibility="private",
    join_requests=True,
    signup_fields=[],
    group_members_visibility=GroupMemberVisibility.managers,
)
GroupPolicies(
    is_high_assurance=False,
    group_visibility="private",
    join_requests=True,
    signup_fields=[],
    group_members_visibility="members",
)
GroupPolicies(
    is_high_assurance=False,
    group_visibility="private",
    join_requests=True,
    signup_fields=[],
    group_members_visibility="managers",
)
GroupPolicies(
    is_high_assurance=False,
    group_visibility="private",
    join_requests=True,
    signup_fields=[],
    group_members_visibility="unknown",  # type: ignore[arg-type]
)
