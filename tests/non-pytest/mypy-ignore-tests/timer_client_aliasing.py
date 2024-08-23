import globus_sdk

c = globus_sdk.TimersClient()
c_legacy = globus_sdk.TimerClient()

# both can call create_timer(<dict>)
c.create_timer({"foo": "bar"})
c_legacy.create_timer({"foo": "bar"})

# both reject create_timer(<non-dict-object>)
c.create_timer(object())  # type: ignore[arg-type]
c_legacy.create_timer(object())  # type: ignore[arg-type]
