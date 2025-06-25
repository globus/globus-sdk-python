from ..collection import StaticScopeCollection, _urn_scope


class _GroupsScopes(StaticScopeCollection):
    resource_server = "groups.api.globus.org"

    all = _urn_scope(resource_server, "all")
    view_my_groups_and_memberships = _urn_scope(
        resource_server, "view_my_groups_and_memberships"
    )


class _NexusScopes(StaticScopeCollection):
    resource_server = "nexus.api.globus.org"

    groups = _urn_scope(resource_server, "groups")


GroupsScopes = _GroupsScopes()
NexusScopes = _NexusScopes()
