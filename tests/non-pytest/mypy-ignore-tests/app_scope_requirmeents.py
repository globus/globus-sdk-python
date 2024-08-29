from globus_sdk.experimental.globus_app import UserApp

# declare scope data in the form of a subtype of the ScopeCollectionType (`list[str]`)
# indexed in a dict, this is meant to be a subtype of the requirements data accepted
# by `GlobusApp.add_scope_requirements`
#
# this is a regression test for that being annotated as `dict[str, ScopeCollectionType]`
# which will reject the input type because `dict` is a mutable container, and therefore
# invariant
scopes: dict[str, list[str]] = {"foo": ["bar"]}
my_app = UserApp("...", client_id="...")
my_app.add_scope_requirements(scopes)
