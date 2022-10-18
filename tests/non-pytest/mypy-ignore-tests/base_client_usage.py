import typing as t

import globus_sdk

# type is (str | None)
s: t.Optional[str] = globus_sdk.BaseClient.resource_server
i: int = globus_sdk.BaseClient.resource_server  # type: ignore [assignment]

# holds on an instance as well
c = globus_sdk.BaseClient()
s = c.resource_server
i = c.resource_server  # type: ignore [assignment]

# check that data:list warns, but other types are okay
r = c.request("POST", "/foo", data="bar")
r = c.request("POST", "/foo", data={})
r = c.request("POST", "/foo", data=list())  # type: ignore [arg-type]
