import uuid

from globus_sdk import AuthClient

zero_id = uuid.UUID(int=0)

# ok usages
ac = AuthClient()
ac.get_identities(ids="foo")
ac.get_identities(ids=zero_id)
ac.get_identities(ids=("foo", "bar"))
ac.get_identities(ids=(zero_id,))
ac.get_identities(usernames="foo,bar")
ac.get_identities(usernames=("foo", "bar"))
ac.get_identities(usernames=("foo", "bar"), provision=True)
ac.get_identities(usernames=("foo", "bar"), query_params={"provision": False})

# bad usage
ac.get_identities(usernames=zero_id)  # type: ignore[arg-type]
ac.get_identities(usernames=(zero_id,))  # type: ignore[arg-type]


# test the response object is iterable
res = ac.get_identities(usernames="foo")
for x in res:
    print(x)
