import typing as t

import globus_sdk

# test that a SpecificFlowClient allows assignments of scope strings and resource_server
# even though the class-level default is a specialized stub object
flow_id = "foo"
specific_flow_client = globus_sdk.SpecificFlowClient(flow_id)

scopes_object = specific_flow_client.scopes
t.assert_type(scopes_object, globus_sdk.scopes.SpecificFlowScopes)

scope: globus_sdk.Scope = scopes_object.user
x: int = scopes_object.user  # type: ignore[assignment]
resource_server: str = specific_flow_client.scopes.resource_server
