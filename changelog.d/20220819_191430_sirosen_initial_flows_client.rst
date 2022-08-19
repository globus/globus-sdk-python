* Add an initial Globus Flows client class, ``globus_sdk.FlowsClient`` (:pr:`NUMBER`)
** ``globus_sdk.FlowsAPIError`` is the error class for this client
** ``FlowsClient.list_flows`` is implemented as a method for listing deployed
   flows, with some of the filtering parameters of this API supported as
   keyword arguments
** The scopes for the Globus Flows API can be accessed via
   ``globus_sdk.scopes.FlowsScopes`` or ``globus_sdk.FlowsClient.scopes``
