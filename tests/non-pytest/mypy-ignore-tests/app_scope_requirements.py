from types import MappingProxyType

from globus_sdk import ClientApp, UserApp

my_user_app = UserApp("...", client_id="...")
my_client_app = ClientApp("...", client_id="...", client_secret="...")

# declare scope data in the form of a subtype of the
# `str | Scope | t.Iterable[str | Scope]` (`list[str]`) indexed in a dict,
# this is meant to be a subtype of the requirements data accepted by
# `GlobusApp.add_scope_requirements`
#
# this is a regression test for that being annotated as
# `dict[str, str | Scope | t.Iterable[str | Scope]]` which will reject the input
# type because `dict` is a mutable container, and therefore invariant
scopes: dict[str, list[str]] = {"foo": ["bar"]}
my_user_app.add_scope_requirements(scopes)
my_client_app.add_scope_requirements(scopes)

# a mapping proxy is an immutable mapping (proxy) and should be accepted by apps as well
# meaning that any mapping is fine, not just `dict` specifically (or MutableMapping)
my_user_app.add_scope_requirements(MappingProxyType(scopes))
my_client_app.add_scope_requirements(MappingProxyType(scopes))


# both of the above tests repeated, but now on init
my_user_app = UserApp("...", client_id="...", scope_requirements=scopes)
my_user_app = UserApp(
    "...", client_id="...", scope_requirements=MappingProxyType(scopes)
)
my_client_app = ClientApp(
    "...", client_id="...", client_secret="...", scope_requirements=scopes
)
my_client_app = ClientApp(
    "...",
    client_id="...",
    client_secret="...",
    scope_requirements=MappingProxyType(scopes),
)
