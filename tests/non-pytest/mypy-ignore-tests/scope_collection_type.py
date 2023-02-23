import globus_sdk
from globus_sdk._types import ScopeCollectionType
from globus_sdk.scopes import MutableScope
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


# this function should type-check okay
def foo(x: ScopeCollectionType) -> str:
    return MutableScope.scopes2str(x)


foo("somestring")
foo(["somestring", "otherstring"])
foo(MutableScope("bar"))
foo((MutableScope("bar"),))
foo({MutableScope("bar"), "baz"})
# bad usages
foo(1)  # type: ignore[arg-type]
foo((False,))  # type: ignore[arg-type]


# now, verify that we can pass scope collections to flow managers
bare_client = globus_sdk.AuthClient()
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes="foo",
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes="foo",
)
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=("foo", "bar"),
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=("foo", "bar"),
)
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=MutableScope("foo"),
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=MutableScope("foo"),
)
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=[MutableScope("foo")],
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=[MutableScope("foo")],
)
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=[MutableScope("foo"), "bar"],
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=[MutableScope("foo"), "bar"],
)
# bad usages
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=1,  # type: ignore[arg-type]
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=1,  # type: ignore[arg-type]
)
GlobusAuthorizationCodeFlowManager(
    bare_client,
    "https://example.org/redirect-uri",
    requested_scopes=none_list,  # type: ignore[arg-type]
)
GlobusNativeAppFlowManager(
    bare_client,
    requested_scopes=none_list,  # type: ignore[arg-type]
)


# furthermore, verify that we can pass these collection types to the client classes
# which wrap the flow managers
# note that oauth2_start_flow allows the scopes as a positional arg
native_client = globus_sdk.NativeAppAuthClient("dummy_client_id")
cc_client = globus_sdk.ConfidentialAppAuthClient(
    "dummy_client_id", "dummy_client_secret"
)

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
native_client.oauth2_start_flow(MutableScope("foo"))
cc_client.oauth2_start_flow("https://example.org/redirect-uri", MutableScope("foo"))
native_client.oauth2_start_flow(requested_scopes=MutableScope("foo"))
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", requested_scopes=MutableScope("foo")
)
native_client.oauth2_start_flow([MutableScope("foo"), "bar"])
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", [MutableScope("foo"), "bar"]
)
native_client.oauth2_start_flow(requested_scopes=[MutableScope("foo"), "bar"])
cc_client.oauth2_start_flow(
    "https://example.org/redirect-uri", requested_scopes=[MutableScope("foo"), "bar"]
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
cc_client.oauth2_client_credentials_tokens(MutableScope("foo"))
cc_client.oauth2_client_credentials_tokens(requested_scopes=MutableScope("foo"))
cc_client.oauth2_client_credentials_tokens([MutableScope("foo"), "bar"])
cc_client.oauth2_client_credentials_tokens(
    requested_scopes=[MutableScope("foo"), "bar"]
)
cc_client.oauth2_client_credentials_tokens(1)  # type: ignore[arg-type]
cc_client.oauth2_client_credentials_tokens(
    requested_scopes=none_list,  # type: ignore[arg-type]
)
