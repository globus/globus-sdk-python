Added
~~~~~

- Add ``app`` as an optional argument to ``BaseClient`` which will accept a
    ``GlobusApp`` to handle authentication, token validation, and token storage when
    using the client.
- Add ``default_scope_requirements`` as an abstract property to ``BaseClient``
    for subclasses to define scopes to automatically be used with an ``app``.
- Add ``add_app_scope`` to ``BaseClient`` as an interface for adding additional
    scope requirements to its ``app``.
- ``AuthClient``, ``FlowsClient``, ``GCSClient``, ``GroupsClient``, ``SearchClient``,
    ``TimerClient``, and ``TransferClient`` all add ``app`` as an optional argument and
    define ``default_scope_requirements`` so that they can be used with a ``GlobusApp``.
- Add ``add_app_data_access_scope`` to ``TransferClient`` as an interface
    for adding a dependent data access scope requirements needed for interacting
    with standard Globus Connect Server mapped collections to its ``app``.
- Add ``get_gcs_info`` as a helper method to ``GCSClient`` for getting information
    from a Globus Connect Server's ``info`` API route.
- Add ``endpoint_client_id`` as a property to ``GCSClient``.


Changed
~~~~~

- ``GCSClient`` instances now have a non-None ``resource_server`` property.
