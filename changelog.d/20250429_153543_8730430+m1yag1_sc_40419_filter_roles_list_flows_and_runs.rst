Added
~~~~~

- ``FlowsClient.list_flows`` and ``FlowsClient.list_runs`` now support the
  ``filter_roles`` parameter to filter results by one or more roles (:pr:`NUMBER`).

Deprecated
~~~~~~~~~~

- ``filter_role`` parameter for ``FlowsClient.list_flows`` is deprecated. Use
  ``filter_roles`` instead (:pr:`NUMBER`).
