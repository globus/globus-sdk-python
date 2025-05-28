import globus_sdk
from globus_sdk._types import ScopeCollectionType
from globus_sdk.scopes import Scope, scopes_to_str
from globus_sdk.services.auth import (
    GlobusAuthorizationCodeFlowManager,
    GlobusNativeAppFlowManager,
)

# in tests below, passing `[None]` inline does not result in an arg-type error
# but instead in a list-item error because mypy effectively identifies that your
# argument type is "correct" (a list or iterable) and that it contains a
# bad item (the None value)
#
# therefore, define the none_list explicitly to control the error behavior better
none_list: list[None] = [None]

# setup clients for usage below
native_client = globus_sdk.NativeAppAuthClient("dummy_client_id")
cc_client = globus_sdk.ConfidentialAppAuthClient(
    "dummy_client_id", "dummy_client_secret"
)


# this function should type-check okay
def foo(x: ScopeCollectionType) -> str:
    return scopes_to_str(x)


foo("somestring")
foo(["somestring", "otherstring"])
foo(Scope("bar"))
foo((Scope("bar"),))
foo({Scope("bar"), "baz"})
# bad usages
foo(1)  # type: ignore[arg-type]
foo((False,))  # type: ignore[arg-type]


# now, verify that we can pass scope collections to flow managers
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes="foo",
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes="foo",
)
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=("foo", "bar"),
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=("foo", "bar"),
)
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=Scope("foo"),
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=Scope("foo"),
)
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=[Scope("foo")],
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=[Scope("foo")],
)
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=[Scope("foo"), "bar"],
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=[Scope("foo"), "bar"],
)
# bad usages
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=1,  # type: ignore[arg-type]
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=1,  # type: ignore[arg-type]
)
GlobusAuthorizationCodeFlowManager(
    cc_client,
    "https://example.org/redirect-uri",
    requested_scopes=none_list,  # type: ignore[arg-type]
)
GlobusNativeAppFlowManager(
    native_client,
    requested_scopes=none_list,  # type: ignore[arg-type]
)


# furthermore, verify that we can pass these collection types to the client classes
# which wrap the flow managers
# note that oauth2_start_flow allows the scopes as a positional arg
native_client.oauth2_start_flow("foo")
cc_client.oauth2_start_flow("https://example.org/redirect-uri", "foo")
native_client.oauth2_start_flow(requested_scopes="foo")
cc_client.oauth2_start_flow("https://example.org/redirect-uri", requested_scopes="foo")
native_client.oauth2_start_flow(("foo", "bar"))
cc_client.oauth2_start_flow("https://example.org/redirect-uri", ("foo", "bar"))
native_client.oauth2_start_flow(requested_scopes=("foo", "bar"))
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", requested_scopes=("foo", "bar")
)
native_client.oauth2_start_flow(Scope("foo"))
cc_client.oauth2_start_flow("https://example.org/redirect-uri", Scope("foo"))
native_client.oauth2_start_flow(requested_scopes=Scope("foo"))
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", requested_scopes=Scope("foo")
)
native_client.oauth2_start_flow([Scope("foo"), "bar"])
cc_client.oauth2_start_flow("https://example.org/redirect-uri", [Scope("foo"), "bar"])
native_client.oauth2_start_flow(requested_scopes=[Scope("foo"), "bar"])
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", requested_scopes=[Scope("foo"), "bar"]
)
# bad usages
native_client.oauth2_start_flow(1)  # type: ignore[arg-type]
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri",
    1,  # type: ignore[arg-type]
)
native_client.oauth2_start_flow(requested_scopes=1)  # type: ignore[arg-type]
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri",
    requested_scopes=1,  # type: ignore[arg-type]
)


# finally, requested_scopes for oauth2_client_credentials_tokens should follow these
# same constraints
cc_client.oauth2_client_credentials_tokens("foo")
cc_client.oauth2_client_credentials_tokens(requested_scopes="foo")
cc_client.oauth2_client_credentials_tokens(("foo", "bar"))
cc_client.oauth2_client_credentials_tokens(requested_scopes=("foo", "bar"))
cc_client.oauth2_client_credentials_tokens(Scope("foo"))
cc_client.oauth2_client_credentials_tokens(requested_scopes=Scope("foo"))
cc_client.oauth2_client_credentials_tokens([Scope("foo"), "bar"])
cc_client.oauth2_client_credentials_tokens(requested_scopes=[Scope("foo"), "bar"])
cc_client.oauth2_client_credentials_tokens(1)  # type: ignore[arg-type]
cc_client.oauth2_client_credentials_tokens(
    requested_scopes=none_list,  # type: ignore[arg-type]
)
