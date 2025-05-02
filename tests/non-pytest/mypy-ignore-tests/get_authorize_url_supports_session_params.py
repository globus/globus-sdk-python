import typing as t
import uuid

import globus_sdk

ac = globus_sdk.AuthLoginClient("someclientid")

# base case
url: str = ac.oauth2_get_authorize_url()


def generate_strs() -> t.Iterator[str]:
    yield "foo"
    yield "bar"


# with session_required_{identities,single_domain,policies} as strings
url = ac.oauth2_get_authorize_url(session_required_identities="foo")
url = ac.oauth2_get_authorize_url(session_required_single_domain="foo")
url = ac.oauth2_get_authorize_url(session_required_policies="foo")
url = ac.oauth2_get_authorize_url(session_message="foo")

# or any iterable of strings
url = ac.oauth2_get_authorize_url(session_required_identities=generate_strs())
url = ac.oauth2_get_authorize_url(session_required_single_domain=generate_strs())
url = ac.oauth2_get_authorize_url(session_required_policies=generate_strs())

# these two support UUIDs
url = ac.oauth2_get_authorize_url(session_required_identities=uuid.uuid4())
url = ac.oauth2_get_authorize_url(session_required_policies=uuid.uuid4())

# now the negative tests, starting with the fact that domain can't take a UUID
url = ac.oauth2_get_authorize_url(
    session_required_single_domain=uuid.uuid4()  # type: ignore[arg-type]
)
url = ac.oauth2_get_authorize_url(
    session_message=uuid.uuid4(),  # type: ignore[arg-type]
)

# integers and other non-str data are not acceptable
url = ac.oauth2_get_authorize_url(
    session_required_identities=1  # type: ignore[arg-type]
)
url = ac.oauth2_get_authorize_url(
    session_required_single_domain=1  # type: ignore[arg-type]
)
url = ac.oauth2_get_authorize_url(session_required_policies=1)  # type: ignore[arg-type]
url = ac.oauth2_get_authorize_url(session_message=1)  # type: ignore[arg-type]
