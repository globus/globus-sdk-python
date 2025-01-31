from ..builder import ScopeBuilder

GroupsScopes = ScopeBuilder(
    "groups.api.globus.org",
    known_scopes=[
        "all",
        "view_my_groups_and_memberships",
    ],
)


NexusScopes = ScopeBuilder(
    "nexus.api.globus.org",
    known_scopes=[
        "groups",
    ],
)
