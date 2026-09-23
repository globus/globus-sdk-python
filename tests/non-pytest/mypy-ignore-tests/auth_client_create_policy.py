import globus_sdk

ac = globus_sdk.AuthClient()

# create new policy with keyword-only args, as supported
ac.create_policy(
    project_id="foo",
    display_name="My Policy",
    description="This is a policy",
)

# create using positional args (deprecated/unsupported)
ac.create_policy(  # type: ignore[call-arg]
    "foo",
    True,  # type: ignore[arg-type]
    101,  # type: ignore[arg-type]
    "My Policy",  # type: ignore[arg-type]
    "This is a policy",  # type: ignore[arg-type]
)
