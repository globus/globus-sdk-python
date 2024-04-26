.. _changelog:

CHANGELOG
=========

.. _changelog_version3:

See :ref:`versioning` for our versioning policy.

The :ref:`upgrading <upgrading>` doc is a good reference if you are upgrading
to a major new version of the SDK.

.. scriv-insert-here

.. _changelog-3.41.0:

v3.41.0 (2024-04-26)
--------------------

Added
~~~~~

- Added a new AuthClient method ``get_consents`` and supporting local data objects.
  These allows a client to poll and interact with the current Globus Auth consent state
  of a particular identity rooted at their client. (:pr:`971`)

- Added ``LoginFlowManager`` and ``CommandLineLoginFLowManager`` to experimental (:pr:`972`)

- Added ``LocalServerLoginFlowManager`` to experimental (:pr:`977`)

- Added support to ``FlowsClient`` for the ``validate_flow`` operation of the
  Globus Flows service. (:pr:`979`)

.. _changelog-3.40.0:

v3.40.0 (2024-04-15)
--------------------

Added
~~~~~

- Add ``globus_sdk.tokenstorage.MemoryAdapter`` for the simplest possible
  in-memory token storage mechanism. (:pr:`964`)

- ``ConfidentialAppAuthClient.oauth2_get_dependent_tokens`` now supports the
  ``scope`` parameter as a string or iterable of strings. (:pr:`965`)

- Moved scope parsing out of experimental. The ``Scope`` construct is now importable from
  the top level `globus_sdk` module. (:pr:`966`)

- Support updating subscriptions assigned to flows in the Flows service. (:pr:`974`)

Development
~~~~~~~~~~~

- Fix concurrency problems in the test suite caused by isort's `.isorted` temporary files. (:pr:`973`)

.. _changelog-3.39.0:

v3.39.0 (2024-03-06)
--------------------

Added
~~~~~

- Added ``TransferClient.operation_stat`` helper method for getting the status of a path on a collection (:pr:`961`)

.. _changelog-3.38.0:

v3.38.0 (2024-03-01)
--------------------

Added
~~~~~

- ``IterableGCSResponse`` and ``UnpackingGCSResponse`` are now available as
  top-level exported names. (:pr:`956`)

- Add ``GroupsClient.get_group_by_subscription_id`` for resolving subscriptions
  to groups. This also expands the ``_testing`` data for ``get_group`` to
  include a subscription group case. (:pr:`957`)

- Added ``prompt`` to the recognized *Globus Authorization Requirements Error*
  ``authorization_parameters`` fields. (:pr:`958`)

.. _changelog-3.37.0:

v3.37.0 (2024-02-14)
--------------------

Added
~~~~~

- All of the basic HTTP methods of ``BaseClient`` and its derived classes which
  accept a ``data`` parameter for a request body, e.g. ``TransferClient.post``
  or ``GroupsClient.put``, now allow the ``data`` to be passed in the form of
  already encoded ``bytes``. (:pr:`951`)

Fixed
~~~~~

- Update ``ensure_datatype`` to work with documents that set ``DATA_TYPE`` to
  ``MISSING`` instead of omitting it (:pr:`952`)

.. _changelog-3.36.0:

v3.36.0 (2024-02-12)
--------------------

Added
~~~~~

- Added support for GCS endpoint get & update operations (:pr:`933`)

  - ``gcs_client.get_endpoint()``
  - ``gcs_client.update_endpoint(EndpointDocument(...))``

- ``TransferClient.endpoint_manager_task_list()`` now supports
  ``filter_endpoint_use`` as a parameter. (:pr:`948`)

- ``FlowsClient.create_flow`` now supports ``subscription_id`` as a parameter.
  (:pr:`949`)

.. _changelog-3.35.0:

v3.35.0 (2024-01-29)
--------------------

Added
~~~~~

- Added a `session_required_mfa` parameter to the `AuthorizationParameterInfo` error
  info object and `oauth2_get_authorize_url` method (:pr:`939`)

Changed
~~~~~~~

- The argument specification for ``AuthClient.create_policy`` was incorrect.
  The corrected method will emit deprecation warnings if called with positional
  arguments, as the corrected version uses keyword-only arguments. (:pr:`936`)

Deprecated
~~~~~~~~~~

- ``TransferClient.operation_symlink`` is now officially deprecated and will
  emit a ``RemovedInV4Warning`` if used. (:pr:`942`)

Fixed
~~~~~

- Included documentation in `AuthorizationParameterInfo` for `session_required_policies`
  (:pr:`939`)

.. _changelog-3.34.0:

v3.34.0 (2024-01-02)
--------------------

Added
~~~~~

- Add the ``delete_protected`` field to ``MappedCollectionDocument``. (:pr:`920`)

Changed
~~~~~~~

- Minor improvements to handling of paths and URLs. (:pr:`922`)

  - Request paths which start with the ``base_path`` of a client are now
    normalized to avoid duplicating the ``base_path``.

  - When a ``GCSClient`` is initialized with an HTTPS URL, if the URL does not
    end with the ``/api`` suffix, that suffix will automatically be appended.
    This allows the ``gcs_manager_url`` field from Globus Transfer to be used
    verbatim as the address for a ``GCSClient``.

Deprecated
~~~~~~~~~~

- ``NativeAppAuthClient.oauth2_validate_token`` and
  ``ConfidentialAppAuthClient.oauth2_validate_token`` have been deprecated, as
  their usage is discouraged by the Auth service. (:pr:`921`)

Development
~~~~~~~~~~~

- Migrate from a CHANGELOG symlink to the RST ``.. include`` directive. (:pr:`918`)

- Tutorial endpoint references are removed from tests and replaced with
  bogus values. (:pr:`919`)

.. _changelog-3.33.0.post0:

v3.33.0.post0 (2023-12-05)
--------------------------

Documentation
~~~~~~~~~~~~~

- Remove references to the Tutorial Endpoints from documentation. (:pr:`915`)

.. _changelog-3.33.0:

v3.33.0 (2023-12-04)
--------------------

Added
~~~~~

- Support custom CA certificate bundles. (:pr:`903`)

  Previously, SSL/TLS verification allowed only a boolean ``True`` or ``False`` value.
  It is now possible to specify a CA certificate bundle file
  using the existing ``verify_ssl`` parameter
  or ``GLOBUS_SDK_VERIFY_SSL`` environment variable.

  This may be useful for interacting with Globus through certain proxy firewalls.

Fixed
~~~~~

- Fix the type annotation for ``globus_sdk.IdentityMap`` init,
  which incorrectly rejected ``ConfidentialAppAuthClient``. (:pr:`912`)

.. _changelog-3.32.0:

v3.32.0 (2023-11-09)
--------------------

Added
~~~~~

.. note::
    These changes pertain to methods of the client objects in the SDK which
    interact with Globus Auth client registration.
    To disambiguate, we refer to the Globus Auth entities below as "Globus Auth
    clients" or specify "in Globus Auth", as appropriate.

- Globus Auth clients objects now have methods for interacting with client and
  project APIs. (:pr:`884`)

  - ``NativeAppAuthClient.create_native_app_instance`` creates a new native app
    instance in Globus Auth for a client.

  - ``ConfidentialAppAuthClient.create_child_client`` creates a child client in
    Globus Auth for a confidential app.

  - ``AuthClient.get_project`` looks up a project.

  - ``AuthClient.get_policy`` looks up a policy document.

  - ``AuthClient.get_policies`` lists all policies in all projects for which
    the current user is an admin.

  - ``AuthClient.create_policy`` creates a new policy.

  - ``AuthClient.update_policy`` updates an existing policy.

  - ``AuthClient.delete_policy`` deletes a policy.

  - ``AuthClient.get_client`` looks up a Globus Auth client by ID or FQDN.

  - ``AuthClient.get_clients`` lists all Globus Auth clients for which the
    current user is an admin.

  - ``AuthClient.create_client`` creates a new client in Globus Auth.

  - ``AuthClient.update_client`` updates an existing client in Globus Auth.

  - ``AuthClient.delete_client`` deletes a client in Globus Auth.

  - ``AuthClient.get_client_credentials`` lists all client credentials for a
    given Globus Auth client.

  - ``AuthClient.create_client_credential`` creates a new client credential for
    a given Globus Auth client.

  - ``AuthClient.delete_client_credential`` deletes a client credential.

  - ``AuthClient.get_scope`` looks up a scope.

  - ``AuthClient.get_scopes`` lists all scopes in all projects for which the
    current user is an admin.

  - ``AuthClient.create_scope`` creates a new scope.

  - ``AuthClient.update_scope`` updates an existing scope.

  - ``AuthClient.delete_scope`` deletes a scope.

- A helper object has been defined for dependent scope manipulation via the
  scopes APIs, ``globus_sdk.DependentScopeSpec`` (:pr:`884`)

Fixed
~~~~~

- When serializing ``TransferTimer`` data, do not convert to UTC if the input
  was a valid datetime with an offset. (:pr:`900`)

.. _changelog-3.31.0:

v3.31.0 (2023-11-01)
--------------------

Added
~~~~~

- Add support for the new Transfer Timer creation method, in the form of a
  client method, ``TimerClient.create_timer``, and a payload builder type,
  ``TransferTimer`` (:pr:`887`)

  - ``create_timer`` only supports dict data and ``TransferTimer``, not the
    previous ``TimerJob`` type

  - Additional helper classes, ``RecurringTimerSchedule`` and
    ``OneceTimerSchedule``, are provided to help build the ``TransferTimer``
    payload

- Request encoding in the SDK will now automatically convert any ``uuid.UUID``
  objects into strings. Previously this was functionality provided by certain
  methods, but now it is universal. (:pr:`892`)

Deprecated
~~~~~~~~~~

- Creation of timers to run transfers using ``TimerJob`` is now
  deprecated (:pr:`887`)

.. _changelog-3.30.0:

v3.30.0 (2023-10-27)
--------------------

Added
~~~~~

- ``TransferClient.operation_ls`` now supports the ``limit`` and ``offset``
  parameters (:pr:`868`)

- A new sentinel value, ``globus_sdk.MISSING``, has been introduced.
  It is used for method calls which need to distinguish missing parameters from
  an explicit ``None`` used to signify ``null`` (:pr:`885`)

  - ``globus_sdk.MISSING`` is now supported in payload data for all methods, and
    will be automatically removed from the payload before sending to the server

Changed
~~~~~~~

- ``GroupPolicies`` objects now treat an explicit instantiation with
  ``high_assurance_timeout=None`` as setting the timeout to ``null`` (:pr:`885`)

.. _changelog-3.29.0:

v3.29.0 (2023-10-12)
--------------------

Changed
~~~~~~~

- The inheritance structure used for Globus Auth client classes has changed.
  (:pr:`849`)

  - A new class, ``AuthLoginClient``, is the base for ``NativeAppAuthClient``
    and ``ConfidentialAppAuthClient``. These classes no longer inherit from
    ``AuthClient``, and therefore no longer inherit certain methods which would
    never succeed if called.

  - ``AuthClient`` is now the only class which provides functionality
    for accessing Globus Auth APIs.

  - ``AuthClient`` no longer includes methods for OAuth 2 login flows which
    would only be valid to call on ``AuthLoginClient`` subclasses.

Deprecated
~~~~~~~~~~

- Several features of Auth client classes are now deprecated. (:pr:`849`)

  - Setting ``AuthClient.client_id`` or accessing it as an attribute
    is deprecated and will emit a warning.

  - ``ConfidentialAppAuthClient.get_identities`` has been preserved as a valid
    call, but will emit a warning. Users wishing to access this API via client
    credentials should prefer to get an access token using a client credential
    callout, and then use that token to call ``AuthClient.get_identities()``.

- The ``AuthClient.oauth2_userinfo`` method has been deprecated in favor of
  ``AuthClient.userinfo``. Callers should prefer the new method name. (:pr:`865`)

.. _changelog-3.28.0:

v3.28.0 (2023-08-30)
--------------------

Python Support
~~~~~~~~~~~~~~

- Add support for Python 3.12. (:pr:`808`)

Added
~~~~~

- Add a ``prompt`` keyword parameter to ``AuthClient.oauth2_get_authorize_url()``. (:pr:`813`)

  Setting this parameter requires users to authenticate with an identity provider,
  even if they are already logged in. Doing so can help avoid errors caused by
  unexpected session required policies, which would otherwise require a second,
  follow-up login flow.

  ``prompt`` could previously only be set via the ``query_params`` keyword parameter.
  It is now more discoverable.

- Add ``TimerClient.pause_job`` and ``TimerClient.resume_job`` for pausing and
  resuming timers. (:pr:`827`)

Documentation
~~~~~~~~~~~~~

- Add an example script which handles creating and running a **flow**. (:pr:`826`)

Development
~~~~~~~~~~~

- Added responses to ``_testing`` reflecting an inactive Timers job (:pr:`828`)

.. _changelog-3.27.0:

v3.27.0 (2023-08-11)
--------------------

Added
~~~~~

- Add a ``FlowsClient.get_run_definition()`` method. (:pr:`799`)

Changed
~~~~~~~

- ``FlowsClient.get_run_logs()`` now uses an ``IterableRunLogsResponse``. (:pr:`797`)

.. _changelog-3.26.0:

v3.26.0 (2023-08-07)
--------------------

Added
~~~~~

- New components are introduced to the experimental subpackage. See the SDK
  Experimental documentation for more details.

  - Add tools which manipulate Globus Auth Requirements error data.
    ``globus_sdk.experimental.auth_requirements_error`` provides a data
    container class, ``GlobusAuthRequirementsError``, and functions for
    converting and validating data against this shape. (:pr:`768`)

  - Introduce an experimental Globus Auth scope parser in
    ``globus_sdk.experimental.scope_parser`` (:pr:`752`)

Changed
~~~~~~~

- The ``scopes`` class attribute of ``SpecificFlowClient`` is now specialized
  to ensure that type checkers will allow access to ``SpecificFlowClient``
  scopes and ``resource_server`` values without ``cast``\ing. The value used is
  a specialized stub which raises useful errors when class-based access is
  performed. The ``scopes`` instance attribute is unchanged. (:pr:`793`)

.. _changelog-3.25.0:

v3.25.0 (2023-07-20)
--------------------

Added
~~~~~

- The ``jwt_params`` argument to ``decode_id_token()`` now allows ``"leeway"``
  to be included to pass a ``leeway`` parameter to pyjwt. (:pr:`790`)

Fixed
~~~~~

- ``decode_id_token()`` defaulted to having no tolerance for clock drift. Slight
  clock drift could lead to JWT claim validation errors. The new default is
  0.5s which should be sufficient for most cases. (:pr:`790`)

Documentation
~~~~~~~~~~~~~

- New scripts in the example gallery demonstrate usage of the Globus Auth
  Developer APIs to List, Create, Delete, and Update Projects. (:pr:`777`)

.. _changelog-3.24.0:

v3.24.0 (2023-07-18)
--------------------

Added
~~~~~

- Add ``FlowsClient.list_runs`` as a method for listing all runs for the
  current user, with support for pagination. (:pr:`782`)

- Add ``SearchClient`` methods for managing search index lifecycle:
  ``create_index``, ``delete_index``, and ``reopen_index`` (:pr:`785`)

Changed
~~~~~~~

- The enforcement logic for URLs in ``BaseClient`` instantiation has been
  improved to only require that ``service_name`` be set if ``base_url`` is not
  provided. (:pr:`786`)

  - This change primarily impacts subclasses, which no longer need to set the
    ``service_name`` class variable if they ensure that the ``base_url`` is
    always passed with a non-null value.

  - Direct instantiation of ``BaseClient`` is now possible, although not
    recommended for most use-cases.

.. _changelog-3.23.0:

v3.23.0 (2023-07-06)
--------------------

Added
~~~~~

- Add ``AuthClient`` methods to support the Projects APIs for listing,
  creating, updating, and deleting projects.

  - ``AuthClient.get_projects`` (:pr:`766`)
  - ``AuthClient.create_project`` (:pr:`772`)
  - ``AuthClient.update_project`` (:pr:`774`)
  - ``AuthClient.delete_project`` (:pr:`776`)

- ``globus_sdk._testing`` now exposes a method, ``construct_error`` which makes
  it simpler to explicitly construct and return a Globus SDK error object for
  testing. This is used in the SDK's own testsuite and is available for
  ``_testing`` users. (:pr:`770`)

- ``AuthClient.oauth2_get_authorize_url`` now supports the following parameters
  for session management: ``session_required_identities``,
  ``session_required_single_domain``, and ``session_required_policies``. Each
  of these accept list inputs, as returned by
  ``ErrorInfo.authorization_parameters``. (:pr:`773`)

Changed
~~~~~~~

* ``AuthClient``, ``NativeAppAuthClient``, and ``ConfidentialAppAuthClient``
  have had their init signatures updated to explicitly list available
  parameters. (:pr:`764`)

  * Type annotations for these classes are now more accurate

  * The ``NativeAppAuthClient`` and ``ConfidentialAppAuthClient`` classes do
    not accept ``authorizer`` in their init signatures. Previously this was
    accepted but raised a ``GlobusSDKUsageError``. Attempting to pass an
    ``authorizer`` will now result in a ``TypeError``.

- ``session_required_policies`` parsing in ``AuthorizationParameterInfo`` now
  supports the policies being returned as a ``list[str]`` in addition to
  supporting ``str`` (:pr:`769`)

Fixed
~~~~~

- ``AuthorizationParameterInfo`` is now more type-safe, and will not return
  parsed data from a response without checking that the data has correct types
  (:pr:`769`)

- Adjust the ``FlowsClient.get_run()`` ``include_flow_description`` parameter
  so it is submitted only when it has a value. (:pr:`778`)

Documentation
~~~~~~~~~~~~~

- The ``_testing`` documentation has been expanded with a dropdown view of the
  response contents for each method. In support of this, client method testing
  docs have been reorganized into a page per service. (:pr:`767`)

.. _changelog-3.22.0:

v3.22.0 (2023-06-22)
--------------------

Added
~~~~~

* Add support for ``AuthClient.get_identity_providers`` for looking up Identity
  Providers by domain or ID in Globus Auth (:pr:`757`)

* Add a method to the Globus Search client, ``SearchClient.batch_delete_by_subject`` (:pr:`760`)

* Add ``AuthScopes.manage_projects`` to scope data. This is also accessible as
  ``AuthClient.scopes.manage_projects`` (:pr:`761`)

Documentation
~~~~~~~~~~~~~

* Alpha features of globus-sdk are now documented in the "Unstable" doc section (:pr:`753`)

.. _changelog-3.21.0:

v3.21.0 (2023-06-16)
--------------------

Added
~~~~~

* ``AuthAPIError`` will now parse a unique ``id`` found in the error
  subdocuments as the ``request_id`` attribute (:pr:`749`)

* Add a ``FlowsClient.update_run()`` method. (:pr:`744`)

* Add a ``FlowsClient.delete_run()`` method. (:pr:`747`)

* Add a ``FlowsClient.cancel_run()`` method. (:pr:`747`)

* Add an ``experimental`` subpackage. (:pr:`751`)

.. _changelog-3.20.1:

v3.20.1 (2023-06-06)
--------------------

Fixed
~~~~~

* Fix ``TransferClient.operation_mkdir`` and ``TransferClient.operation_rename`` to no
  longer send null ``local_user`` by default (:pr:`741`)

.. _changelog-3.20.0:

v3.20.0 (2023-06-05)
--------------------

Added
~~~~~

* Implemented ``FlowsClient.get_run(...)`` (:pr:`721`)

* Implemented ``FlowsClient.get_run_logs(...)`` (:pr:`722`)

* Implemented ``SpecificFlowClient.resume_run(...)`` (:pr:`723`)

* ``ConsentRequiredInfo`` now accepts ``required_scope`` (singular) containing
  a single string as an alternative to ``required_scopes``. However, it will
  parse both formats into a ``required_scopes`` list. (:pr:`726`)

* ``FlowsClient.list_flows`` now supports passing a non-string iterable of
  strings to ``orderby`` in order to indicate multiple orderings (:pr:`730`)

* Support ``pathlib.Path`` objects as filenames for the JSON and sqlite token
  storage adapters. (:pr:`734`)

* Several ``TransferClient`` methods, ``TransferData``, and ``DeleteData`` now
  support the ``local_user``, ``source_local_user``, and
  ``destination_local_user`` parameters  (:pr:`736`)

Changed
~~~~~~~

* Behavior has changed slightly specifically for ``TimerAPIError``. When parsing
  fails, the ``code`` will be ``Error`` and the ``messages`` will be empty. The
  ``detail`` field will be treated as the ``errors`` array for these errors
  when it is present and contains an array of objects.

* Error parsing in the SDK has been enhanced to better support JSON:API and
  related error formats with multiple sub-errors. Several attributes are
  added or changed. For most SDK users, the changes will be completely
  transparent or a minor improvement. (:pr:`725`)

  * Error parsing now attempts to detect the format of the error data and will
    parse JSON:API data differently from non-JSON:API data. Furthermore,
    parsing is stricter about the expectations about fields and their types.
    JSON:API parsing now has its own distinct parsing path, followed only when
    the JSON:API mimetype is present.

  * A new attribute is added to API error objects, ``errors``. This is a list
    of subdocuments parsed from the error data, especially relevant for
    JSON:API errors and similar formats. See the
    :ref:`ErrorSubdocument documentation <error_subdocuments>` for details.

  * A new attribute is now present on API error objects, ``messages``. This is
    a list of messages parsed from the error data, for errors with multiple
    messages. When there is only one message, ``messages`` will only contain
    one item.

  * The ``message`` field is now an alias for a joined string of
    ``messages``. Assigning a string to ``message`` is supported for error
    subclasses, but is deprecated.

  * ``message`` will now be ``None`` when no messages can be parsed from the error data.
    Previously, the default for ``message`` would be an alias for ``text``.

  * All error types now support ``request_id`` as an attribute, but it will
    default to ``None`` for errors which do not include a ``request_id``.

  * An additional field is checked by default for error message data,
    ``title``. This is useful when errors contain ``title`` but no
    ``detail`` field. The extraction of messages from errors has been made
    stricter, especially in the JSON:API case.

  * The ``code`` field of errors will no longer attempt to parse only the first
    ``code`` from multiple sub-errors. Instead, ``code`` will first parse a
    top-level ``code`` field, and then fallback to checking if *all* sub-errors
    have the same ``code`` value. The result is that certain errors which would
    populate a non-default ``code`` value no longer will, but the ``code`` will
    also no longer be misleading when multiple errors with different codes are
    present in an error object.

  * The ``code`` field of an error may now be ``None``. This is specifically
    possible when the error format is detected to be known as JSON:API and
    there is no ``code`` present in any responses.

Fixed
~~~~~

* The TransferRequestsTransport will no longer automatically retry errors with a code of EndpointError

* Fix pagination on iterable gcs client routes  (:pr:`738`, :pr:`739`)

  * ``GCSClient.get_storage_gateway_list``

  * ``GCSClient.get_role_list``

  * ``GCSClient.get_collection_list``

  * ``GCSClient.get_user_credential_list``


.. _changelog-3.19.0:

v3.19.0 (2023-04-14)
--------------------

Added
~~~~~

* Added ``FlowsClient.update_flow(...)`` (:pr:`710`)

* Support passing "include" as a transfer ``filter_rule`` method (:pr:`712`)

* Make the request-like interface for response objects and errors more uniform. (:pr:`715`)

  * Both ``GlobusHTTPResponse`` and ``GlobusAPIError`` are updated to ensure
    that they have the following properties in common: ``http_status``,
    ``http_reason``, ``headers``, ``content_type``, ``text``

  * ``GlobusHTTPResponse`` and ``GlobusAPIError`` have both gained a new
    property, ``binary_content``, which returns the unencoded response data as
    bytes

Deprecated
~~~~~~~~~~

* ``GlobusAPIError.raw_text`` is deprecated in favor of ``text``

Fixed
~~~~~

* The return type of ``AuthClient.get_identities`` is now correctly annotated as
  an iterable type, ``globus_sdk.GetIdentitiesResponse`` (:pr:`716`)

Documentation
~~~~~~~~~~~~~

* Documentation for client methods has been improved to more consistently
  format and display examples and other information (:pr:`714`)

.. _changelog-3.18.0:

v3.18.0 (2023-03-16)
--------------------

Added
~~~~~

* ``ConfidentialAppAuthClient.oauth2_get_dependent_tokens`` now supports the
  ``refresh_tokens`` parameter to enable requests for dependent refresh tokens (:pr:`698`)

Changed
~~~~~~~

* Behaviors which will change in version 4.0.0 of the ``globus-sdk`` now emit
  deprecation warnings.

* ``TransferData.add_item`` now defaults to omitting ``recursive`` rather than
  setting its value to ``False``. This change better matches new Transfer API
  behaviors which treat the absence of the ``recursive`` flag as meaning
  autodetect, rather than the previous default of ``False``. Setting the
  recursive flag can still have beneficial behaviors, but should not be
  necessary for many use-cases (:pr:`696`)

Deprecated
~~~~~~~~~~

* Omitting ``requested_scopes`` or specifying it as ``None`` is now deprecated
  and will emit a warning. In version 4, users will always be required to
  specify their scopes when performing login flows. This applies to the
  following methods:

  * ``ConfidentialAppAuthClient.oauth2_client_credentials_tokens``
  * ``AuthClient.oauth2_start_flow``

* ``SearchClient.update_entry`` and ``SearchClient.create_entry`` are
  officially deprecated and will emit a warning. These APIs are aliases of
  ``SearchClient.ingest``, but their existence has caused confusion. Users are
  encouraged to switch to ``SearchClient.ingest`` instead (:pr:`695`)

Fixed
~~~~~

* When users input empty ``requested_scopes`` values, these are now rejected
  with a usage error instead of being translated into the default set of
  ``requested_scopes``

* Fix the type annotation for `max_sleep` on client transports to allow `float`
  values (:pr:`697`)

.. _changelog-3.17.0:

v3.17.0 (2023-02-27)
--------------------

Python Support
~~~~~~~~~~~~~~

* Remove support for python3.6 (:pr:`681`)

Added
~~~~~

* ``MutableScope`` objects can now be used in the ``oauth2_start_flow`` and
  ``oauth2_client_credentials_tokens`` methods of ``AuthClient`` classes as part
  of ``requested_scopes`` (:pr:`689`)

Changed
~~~~~~~

* Make ``MutableScope.scope_string`` a public instance attribute (was
  ``_scope_string``) (:pr:`687`)

* Globus Groups methods which required enums as arguments now also accept
  a variety of ``Literal`` strings in their annotations as well. This is
  coupled with changes to ensure that strings and enums are always serialized
  correctly in these cases. (:pr:`691`)

Fixed
~~~~~

* Fix a typo in ``TransferClient.endpoint_manager_task_successful_transfers``
  which prevented calls from being made correctly (:pr:`683`)

.. _changelog-3.16.0:

v3.16.0 (2023-02-07)
--------------------

Added
~~~~~

* Allow UUID values for the ``client_id`` parameter to ``AuthClient`` and its
  subclasses (:pr:`676`)

Changed
~~~~~~~

* Improved GCS Collection datatype detection to support ``collection#1.6.0``
  and ``collection#1.7.0`` documents (:pr:`675`)

  * ``guest_auth_policy_id`` is now supported on ``MappedCollectionDcoument``

  * ``user_message`` strings over 64 characters are now supported

* The ``session_required_policies`` attribute of ``AuthorizationInfo`` is now
  parsed as a list of strings when present, and ``None`` when absent. (:pr:`678`)

* ``globus_sdk.ArrayResponse`` and ``globus_sdk.IterableResponse`` are now
  available as names. Previously, these were only importable from
  ``globus_sdk.response`` (:pr:`680`)

Fixed
~~~~~

* ``ArrayResponse`` and ``IterableResponse`` have better error behaviors when
  the API data does not match their expected types (:pr:`680`)

Documentation
~~~~~~~~~~~~~

* Fix the Timer code example (:pr:`672`)

* New documentation examples for Transfer Task submission in the presence of
  ``ConsentRequired`` errors (:pr:`673`)

.. _changelog-3.15.1:

v3.15.1 (2022-12-13)
--------------------

Added
~~~~~

* AuthorizationParameterInfo now exposes session_required_policies (:pr:`658`)

Fixed
~~~~~

* Fix a bug where ``TransferClient.endpoint_manager_task_list`` didn't handle
  the ``last_key`` argument when paginated (:pr:`662`)

.. _changelog-3.15.0:

v3.15.0 (2022-11-22)
--------------------

Added
~~~~~

* Scope Names can be set explicitly in a ``ScopeBuilder`` (:pr:`641`)

* Introduced ``ScopeBuilder.scope_names`` property (:pr:`641`)

* Add support for ``interpret_globs`` and ``ignore_missing`` to ``DeleteData`` (:pr:`646`)

* A new object, ``globus_sdk.LocalGlobusConnectServer`` can be used to inspect
  the local installation of Globus Connect Server (:pr:`647`)

  * The object supports properties for ``endpoint_id`` and ``domain_name``

  * This only supports Globus Connect Server version 5

* The filter argument to TransferClient.operation_ls now accepts a list to pass
  multiple filter params (:pr:`652`)

* Improvements to ``MutableScope`` objects (:pr:`654`)

  * ``MutableScope(...).serialize()`` is added, and ``str(MutableScope(...))`` uses it

  * ``MutableScope.add_dependency`` now supports ``MutableScope`` objects as inputs

  * ``ScopeBuilder.make_mutable`` now accepts a keyword argument ``optional``.
    This allows, for example, ``TransferScopes.make_mutable("all", optional=True)``

Changed
~~~~~~~

* Improve the ``__str__`` implementation for ``OAuthTokenResponse`` (:pr:`640`)

* When ``GlobusHTTPResponse`` contains a list, calls to ``get()`` will no
  longer fail with an ``AttributeError`` but will return the default value
  (``None`` if unspecified) instead (:pr:`644`)

Deprecated
~~~~~~~~~~

* The ``optional`` argument to ``add_dependency`` is deprecated.
  ``MutableScope(...).add_dependency(MutableScope("foo", optional=True))``
  can be used to add an optional dependency

Fixed
~~~~~

* Fixed SpecificFlowClient scope string (:pr:`641`)

* Fix a bug in the type annotations for transport objects which restricted the
  size of status code tuples set as classvars (:pr:`651`)

.. _changelog-3.14.0:

v3.14.0 (2022-11-01)
--------------------

Python Support
~~~~~~~~~~~~~~

* Python 3.11 is now officially supported (:pr:`628`)

Added
~~~~~

* Add support for ``FlowsClient.get_flow`` and ``FlowsClient.delete_flow``
  (:pr:`631`, :pr:`626`)

* Add a ``close()`` method to ``SQLiteAdapter`` which closes the underlying
  connection (:pr:`628`)

.. _changelog-3.13.0:

v3.13.0 (2022-10-13)
--------------------

Added
~~~~~

* Add ``connect_params`` to ``SQLiteAdapter``, enabling customization of the
  sqlite connection (:pr:`613`)

* Add ``FlowsClient.create_flow(...)`` (:pr:`614`)

* Add ``globus_sdk.SpecificFlowClient`` to manage interactions performed against
  a specific flow (:pr:`616`)

* Add support to ``FlowsClient.list_flows`` for pagination and the ``orderby``
  parameter (:pr:`621`, :pr:`622`)

Documentation
~~~~~~~~~~~~~

* Fix rst formatting for a few nested bullet points in existing changelog (:pr:`619`)

.. _changelog-3.12.0:

v3.12.0 (2022-09-21)
--------------------

Added
~~~~~

* Add Mapped Collection policy helper types for constructing ``policies`` data. (:pr:`607`)
  The following new types are introduced:

  * ``CollectionPolicies`` (the base class for these types)
  * ``POSIXCollectionPolicies``
  * ``POSIXStagingCollectionPolicies``
  * ``GoogleCloudStorageCollectionPolicies``

Fixed
~~~~~

* Fix bug where ``UserCredential`` policies were being converted to a string (:pr:`608`)

* Corrected the Flows service ``resource_server`` string to ``flows.globus.org`` (:pr:`612`)

.. _changelog-3.11.0:

v3.11.0 (2022-08-30)
--------------------

Added
~~~~~

* Implement ``__dir__`` for the lazy importer in ``globus_sdk``. This
  enables tab completion in the interpreter and other features with
  rely upon ``dir(globus_sdk)`` (:pr:`603`)

* Add an initial Globus Flows client class, ``globus_sdk.FlowsClient`` (:pr:`604`)

  * ``globus_sdk.FlowsAPIError`` is the error class for this client
  * ``FlowsClient.list_flows`` is implemented as a method for listing deployed
    flows, with some of the filtering parameters of this API supported as
    keyword arguments
  * The scopes for the Globus Flows API can be accessed via
    ``globus_sdk.scopes.FlowsScopes`` or ``globus_sdk.FlowsClient.scopes``

Changed
~~~~~~~

* Adjust behaviors of ``TransferData`` and ``TimerJob`` to make
  ``TimerJob.from_transfer_data`` work and to defer requesting the
  ``submission_id`` until the task submission call (:pr:`602`)

  * ``TransferData`` avoids passing ``null`` for several values when they are
    omitted, ranging from optional parameters to ``add_item`` to
    ``skip_activation_check``

  * ``TransferData`` and ``DeleteData`` now support usage in which the
    ``transfer_client`` parameters is ``None``. In these cases, if
    ``submission_id`` is omitted, it will be omitted from the document,
    allowing the creation of a partial task submsision document with no
    ``submission_id``

  * ``TimerJob.from_transfer_data`` will now raise a ``ValueError`` if the input
    document contains ``submission_id`` or ``skip_activation_check``

  * ``TransferClient.submit_transfer`` and ``TransferClient.submit_delete`` now
    check to see if the data being sent contains a ``submission_id``. If it does
    not, ``get_submission_id`` is called automatically and set as the
    ``submission_id`` on the payload. The new ``submission_id`` is set on the
    object passed to these methods, meaning that these methods are now
    side-effecting.

The newly recommended usage for ``TransferData`` and ``DeleteData`` is to pass
the endpoints as named parameters:

.. code-block:: python

    # -- for TransferData --
    # old usage
    transfer_client = TransferClient()
    transfer_data = TransferData(transfer_client, ep1, ep2)
    # new (recommended) usage
    transfer_data = TransferData(source_endpoint=ep1, destination_endpoint=ep2)

    # -- for DeleteData --
    # old usage
    transfer_client = TransferClient()
    delete_data = TransferData(transfer_client, ep)
    # new (recommended) usage
    delete_data = DeleteData(endpoint=ep)

.. _changelog-3.10.1:

v3.10.1 (2022-07-11)
--------------------

Changed
~~~~~~~

* Use ``setattr`` in the lazy-importer. This makes attribute access after
  imports faster by several orders of magnitude. (:pr:`591`)

Documentation
~~~~~~~~~~~~~

* Add guest collection example script to docs (:pr:`590`)

.. _changelog-3.10.0:

v3.10.0 (2022-06-27)
--------------------

Removed
~~~~~~~

* Remove nonexistent ``monitor_ongoing`` scope from ``TransferScopes`` (:pr:`583`)

Added
~~~~~

* Add User Credential methods to ``GCSClient`` (:pr:`582`)

  * ``get_user_credential_list``
  * ``get_user_credential``
  * ``create_user_credential``
  * ``update_user_credential``
  * ``delete_user_credential``

* Add ``connector_id_to_name`` helper to ``GCSClient`` to resolve GCS Connector
  UUIDs to human readable Connector display names (:pr:`582`)

.. _changelog-3.9.0:

v3.9.0 (2022-06-02)
-------------------

Added
~~~~~

* Add helper objects and methods for interacting with Globus Connect Server
  Storage Gateways (:pr:`554`)

  * New methods on ``GCSClient``: ``create_storage_gateway``, ``get_storage_gateway``,
    ``get_storage_gateway_list``, ``update_storage_gateway``,
    ``delete_storage_gateway``

  * New helper classes for constructing storage gateway documents.
    ``StorageGatewayDocument`` is the main one, but also
    ``POSIXStoragePolicies`` and ``POSIXStagingStoragePolicies`` are added for
    declaring the storage gateway ``policies`` field. More policy helpers will
    be added in future versions.

* Add support for more ``StorageGatewayPolicies`` documents. (:pr:`562`)
  The following types are now available:

  * ``BlackPearlStoragePolicies``
  * ``BoxStoragePolicies``
  * ``CephStoragePolicies``
  * ``GoogleDriveStoragePolicies``
  * ``GoogleCloudStoragePolicies``
  * ``OneDriveStoragePolicies``
  * ``AzureBlobStoragePolicies``
  * ``S3StoragePolicies``
  * ``ActiveScaleStoragePolicies``
  * ``IrodsStoragePolicies``
  * ``HPSSStoragePolicies``

* Add ``https`` scope to ``GCSCollectionScopeBuilder`` (:pr:`563`)

* ``ScopeBuilder`` objects now implement ``__str__`` for easy viewing.
  For example, ``print(globus_sdk.TransferClient.scopes)`` (:pr:`568`)

* Several improvements to Transfer helper objects (:pr:`573`)

  * Add ``TransferData.add_filter_rule`` for adding filter rules (exclude
    rules) to transfers

  * Add ``skip_activation_check`` as an argument to ``DeleteData`` and
    ``TransferData``

  * The ``sync_level`` argument to ``TransferData`` is now annotated more
    accurately to reject bad strings

Changed
~~~~~~~

* Update the fields used to extract ``AuthAPIError`` messages (:pr:`566`)

* Imports from ``globus_sdk`` are now evaluated lazily via module-level
  ``__getattr__`` on python 3.7+ (:pr:`571`)

  * This improves the performance of imports for almost all use-cases, in some
    cases by over 80%

  * The method ``globus_sdk._force_eager_imports()`` can be used to force
    non-lazy imports, for latency sensitive applications which wish to control
    when the time cost of import evaluation is paid. This method is private and is
    therefore is not covered under the ``globus-sdk``'s SemVer guarantees, but it is
    expected to remain stable for the foreseeable future.

* Improve handling of array-style API responses (:pr:`575`)

  * Response objects now define ``__bool__`` as ``bool(data)``. This
    means that ``bool(response)`` could be ``False`` if the data is ``{}``,
    ``[]``, ``0``, or other falsey-types. Previously,
    ``__bool__`` was not defined, meaning it was always ``True``

  * ``globus_sdk.response.ArrayResponse`` is a new class which describes
    responses which are expected to hold a top-level array. It satisfies the
    sequence protocol, allowing indexing with integers and slices, iteration
    over the array data, and length checking with ``len(response)``

  * ``globus_sdk.GroupsClient.get_my_groups`` returns an ``ArrayResponse``,
    meaning the response data can now be iterated and otherwise used

.. _changelog-3.8.0:

v3.8.0 (2022-05-04)
-------------------

Added
~~~~~

* Several changes expose more details of HTTP requests (:pr:`551`)

  * ``GlobusAPIError`` has a new property ``headers`` which provides the
    case-insensitive mapping of header values from the response

  * ``GlobusAPIError`` and ``GlobusHTTPResponse`` now include ``http_reason``,
    a string property containing the "reason" from the response

  * ``BaseClient.request`` and ``RequestsTransport.request`` now have options
    for setting boolean options ``allow_redirects`` and ``stream``, controlling
    how requests are processed

* New tools for working with optional and dependent scope strings (:pr:`553`)

  * A new class is provided for constructing optional and dependent scope
    strings, ``MutableScope``. Import as in
    ``from globus_sdk.scopes import MutableScope``

  * ``ScopeBuilder`` objects provide a method, ``make_mutable``, which converts
    from a scope name to a ``MutableScope`` object. See documentation on scopes
    for usage details

.. _changelog-3.7.0:

v3.7.0 (2022-04-08)
-------------------

Added
~~~~~

* Add a client for the Timer service (:pr:`548`)

  * Add ``TimerClient`` class, along with ``TimerJob`` for constructing data
    to pass to the Timer service for job creation, and ``TimerAPIError``
  * Modify ``globus_sdk.config`` utilities to provide URLs for Actions and
    Timer services

Fixed
~~~~~

* Fix annotations to allow request data to be a string. This is
  supported at runtime but was missing from annotations. (:pr:`549`)

.. _changelog-3.6.0:

v3.6.0 (2022-03-18)
-------------------

Added
~~~~~

* ``ScopeBuilder`` objects now support ``known_url_scopes``, and known scope
  arguments to a ``ScopeBuilder`` may now be of type ``str`` in addition to
  ``list[str]`` (:pr:`536`)

* Add the ``RequestsTransport.tune`` contextmanager to the transport layer,
  allowing the settings on the transport to be set temporarily (:pr:`540`)

.. _changelog-3.5.0:

v3.5.0 (2022-03-02)
-------------------

Added
~~~~~

* ``globus_sdk.IdentityMap`` can now take a cache as an input. This allows
  multiple ``IdentityMap`` instances to share the same storage cache. Any
  mutable mapping type is valid, so the cache can be backed by a database or
  other storage (:pr:`500`)

* Add support for ``include`` as a parameter to ``GroupsClient.get_group``.
  ``include`` can be a string or iterable of strings (:pr:`528`)

* Add a new method to tokenstorage, ``SQLiteAdapter.iter_namespaces``, which
  iterates over all namespaces visible in the token database (:pr:`529`)

Changed
~~~~~~~

* Add ``TransferRequestsTransport`` class that does not retry ExternalErrors.
  This fixes cases in which the ``TransferClient`` incorrectly retried requests (:pr:`522`)

* Use the "reason phrase" as a failover for stringified API errors with no body (:pr:`524`)

Documentation
~~~~~~~~~~~~~

* Enhance documentation for all of the parameters on methods of ``GroupsClient``

.. _changelog-3.4.2:

v3.4.2 (2022-02-18)
-------------------

Fixed
~~~~~

* Fix the pagination behavior for ``TransferClient`` on ``task_skipped_errors`` and
  ``task_successful_transfers``, and apply the same fix to the endpoint manager
  variants of these methods. Prior to the fix, paginated calls would return a
  single page of results and then stop (:pr:`520`)

.. _changelog-3.4.1:

v3.4.1 (2022-02-11)
-------------------

Fixed
~~~~~

* The ``typing_extensions`` requirement in package metadata now sets a lower
  bound of ``4.0``, to force upgrades of installations to get a new enough version
  (:pr:`518`)

.. _changelog-3.4.0:

v3.4.0 (2022-02-11)
-------------------

Added
~~~~~

* Support pagination on ``SearchClient.post_search`` (:pr:`507`)

* Add support for scroll queries to ``SearchClient``. ``SearchClient.scroll``
  and ``SearchClient.paginated.scroll`` are now available as methods, and a new
  helper class, ``SearchScrollQuery``, can be used to easily construct
  scrolling queries. (:pr:`507`)

* Add methods to ``SearchClient`` for managing index roles. ``create_role``,
  ``delete_role``, and ``get_role_list`` (:pr:`507`)

* Add ``mapped_collection`` and ``filter`` query arguments to ``GCSClient.get_collection_list`` (:pr:`510`)

* Add role methods to ``GCSClient`` (:pr:`513`)

  * ``GCSClient.get_role_list`` lists endpoint or collection roles
  * ``GCSClient.create_role`` creates a role
  * ``GCSClient.get_role`` gets a single role
  * ``GCSClient.delete_role`` deletes a role

* The response from ``AuthClient.get_identities`` now supports iteration,
  returning results from the ``"identities"`` array (:pr:`514`)

.. _changelog-3.3.1:

v3.3.1 (2022-01-25)
-------------------

Fixed
~~~~~

* Packaging bugfix. ``globus-sdk`` is now built with pypa's ``build`` tool, to
  resolve issues with wheel builds.

.. _changelog-3.3.0:

v3.3.0 (2022-01-25)
-------------------

Added
~~~~~

* Add ``update_group`` method to ``GroupsClient`` (:pr:`506`)

* The ``TransferData`` and ``DeleteData`` helper objects now accept the
  following parameters: ``notify_on_succeeded``, ``notify_on_failed``, and
  ``notify_on_inactive``. All three are boolean parameters with a default
  of ``True``. (:pr:`502`)

* Add ``Paginator.wrap`` as a method for getting a paginated methods. This interface is more
  verbose than the existing ``paginated`` methods, but correctly preserves type
  annotations. It is therefore preferable for users who are using ``mypy`` to do
  type checking. (:pr:`494`)

Changed
~~~~~~~

* ``Paginator`` objects are now generics over a type var for their page type. The
  page type is bounded by ``GlobusHTTPResponse``, and most type-checker behaviors
  will remain unchanged (:pr:`495`)

Fixed
~~~~~

* Several minor bugs have been found and fixed (:pr:`504`)

  * Exceptions raised in the SDK always use ``raise ... from`` syntax where
    appropriate. This corrects exception chaining in the local endpoint and
    several response objects.

  * The encoding of files opened by the SDK is now always ``UTF-8``

  * ``TransferData`` will now reject unsupported ``sync_level`` values with a
    ``ValueError`` on initialization, rather than erroring at submission time.
    The ``sync_level`` has also had its type annotation fixed to allow for
    ``int`` values.

  * Several instances of undocumented parameters have been discovered, and these
    are now rectified.

Documentation
~~~~~~~~~~~~~

* Document ``globus_sdk.config.get_service_url`` and ``globus_sdk.config.get_webapp_url``
  (:pr:`496`)

  * Internally, these are updated to be able to default to the ``GLOBUS_SDK_ENVIRONMENT`` setting,
    so specifying an environment is no longer required

.. _changelog-3.2.1:

v3.2.1 (2021-12-13)
-------------------

Python Support
~~~~~~~~~~~~~~

* Update to avoid deprecation warnings on python 3.10 (:pr:`499`)

.. _changelog-3.2.0:

v3.2.0 (2021-12-02)
-------------------

Added
~~~~~

* Add ``iter_items`` as a method on ``TransferData`` and ``DeleteData`` (:pr:`488`)

* Add the `resource_server` property to client classes and objects. For example,
  `TransferClient.resource_server` and `GroupsClient().resource_server` are now usable
  to get the resource server string for the relevant services. `resource_server` is
  documented as part of `globus_sdk.BaseClient` and may be `None`. (:pr:`489`)

* The implementation of several properties of ``GlobusHTTPResponse`` has
  changed (:pr:`497`)

  * Responses have a new property, ``headers``, a case-insensitive
    dict of headers from the response

  * Responses now implement ``http_status`` and ``content_type`` as
    properties without setters

Changed
~~~~~~~

* ClientCredentialsAuthorizer now accepts ``Union[str, Iterable[str]]``
  as the type for scopes (:pr:`498`)

Fixed
~~~~~

* Fix type annotations on client methods with paginated variants (:pr:`491`)

.. _changelog-3.1.0:

v3.1.0 (2021-10-13)
-------------------

Added
~~~~~

* Add ``filter`` as a supported parameter to ``TransferClient.task_list`` (:pr:`484`)

* The ``filter`` parameter to ``TransferClient.task_list`` and
  ``TransferClient.operation_ls`` can now be passed as a ``Dict[str, str | List[str]]``.
  Documentation on the ``TransferClient`` explains how this will be formatted,
  and is linked from the param docs for ``filter`` on each method (:pr:`484`)

Changed
~~~~~~~

* Adjust package metadata for `cryptography` dependency, specifying
  `cryptography>=3.3.1` and no upper bound. This is meant to help mitigate
  issues in which an older `cryptography` version is installed gets used in
  spite of it being incompatible with `pyjwt[crypto]>=2.0` (:pr:`486`)

.. _changelog-3.0.3:

v3.0.3 (2021-10-11)
-------------------

Fixed
~~~~~

* Fix several internal decorators which were destroying type information about
  decorated functions. Type signatures of many methods are therefore corrected (:pr:`485`)

.. _changelog-3.0.2:

v3.0.2 (2021-09-29)
-------------------

Changed
~~~~~~~

* Produce more debug logging when SDK logs are enabled (:pr:`480`)

Fixed
~~~~~

* Update the minimum dependency versions to lower bounds which are verified to
  work with the testsuite (:pr:`482`)

.. _changelog-3.0.1:

v3.0.1 (2021-09-15)
-------------------

Added
~~~~~

* ``ScopeBuilder`` objects now define the type of ``__getattr__`` for ``mypy`` to
  know that dynamic attributes are strings (:pr:`472`)

Fixed
~~~~~

* Fix malformed PEP508 ``python_version`` bound in dev dependencies (:pr:`474`)

Development
~~~~~~~~~~~

* Fix remaining ``type: ignore`` usages in globus-sdk (:pr:`473`)

.. _changelog-3.0.0:

v3.0.0 (2021-09-14)
-------------------

Removed
~~~~~~~

* Remove support for ``bytes`` values for fields consuming UUIDs (:pr:`471`)

Added
~~~~~

* Add ``filter_is_error`` parameter to advanced task list (:pr:`467`)

* Add a ``LocalGlobusConnectPersonal.get_owner_info()`` for looking up local
  user information from gridmap (:pr:`466`)

* Add support for GCS collection create and update. This includes new data
  helpers, ``MappedCollectionDcoument`` and ``GuestCollectionDocument`` (:pr:`468`)

* Add support for specifying ``config_dir`` to ``LocalGlobusConnectPersonal`` (:pr:`470`)

.. _changelog-3.0.0b4:

v3.0.0b4 (2021-09-01)
---------------------

Removed
~~~~~~~

* Remove ``BaseClient.qjoin_path`` (:pr:`452`)

Added
~~~~~

* Add a new ``GCSClient`` class for interacting with GCS Manager APIs
  (:pr:`447`)

* ``GCSClient`` supports ``get_collection`` and ``delete_collection``.
  ``get_collection`` uses a new ``UnpackingGCSResponse`` response type (:pr:`451`,
  :pr:`464`)

* Add ``delete_destination_extra`` param to ``TransferData`` (:pr:`456`)

* ``TransferClient.endpoint_manager_task_list`` now takes filters as named
  keyword arguments, not only in ``query_params`` (:pr:`460`)

Changed
~~~~~~~

* Rename ``GCSScopeBuilder`` to ``GCSCollectionScopeBuilder`` and add
  ``GCSEndpointScopeBuilder``. The ``GCSClient`` includes helpers for
  instantiating these scope builders (:pr:`448`)

* The ``additional_params`` parameter to ``AuthClient.oauth2_get_authorize_url``
  has been renamed to ``query_params`` for consistency with other methods (:pr:`453`)

* Enforce keyword-only arguments for most SDK-provided APIs (:pr:`453`)

* All type annotations for ``Sequence`` which could be relaxed to ``Iterable``
  have been updated (:pr:`465`)

Fixed
~~~~~

* Minor fix to wheel builds: do not declare wheels as universal (:pr:`444`)

* Fix annotations for ``server_id`` on ``TransferClient`` methods (:pr:`455`)

* Fix ``visibility`` typo in ``GroupsClient`` (:pr:`463`)

Documentation
~~~~~~~~~~~~~

* Ensure all ``TransferClient`` method parameters are documented (:pr:`449`,
  :pr:`454`, :pr:`457`, :pr:`458`, :pr:`459`, :pr:`461`, :pr:`462`)

.. _changelog-3.0.0b3:

v3.0.0b3 (2021-08-13)
---------------------

Added
~~~~~

* Flesh out the ``GroupsClient`` and add helpers for interacting with the
  Globus Groups service, including enumerated constants, payload builders, and
  a high-level client for doing non-batch operations called the
  ``GroupsManager`` (:pr:`435`, :pr:`443`)

* globus-sdk now provides much more complete type annotations coverage,
  allowing type checkers like ``mypy`` to catch a much wider range of usage
  errors (:pr:`442`)

.. _changelog-3.0.0b2:

v3.0.0b2 (2021-07-16)
---------------------

Added
~~~~~

* Add scope constants and scope construction helpers. See new documentation on
  :ref:`scopes and ScopeBuilders <scopes>` for details (:pr:`437`, :pr:`440`)

* API Errors now have an attached ``info`` object with parsed error data where
  applicable. See the :ref:`ErrorInfo documentation <error_info>` for details
  (:pr:`441`)

Changed
~~~~~~~

* Improve the rendering of API exceptions in stack traces to include the
  method, URI, and authorization scheme (if recognized) (:pr:`439`)

* Payload helper objects (``TransferData``, ``DeleteData``, and ``SearchQuery``)
  now inherit from a custom object, not ``dict``, but they are still dict-like in
  behavior (:pr:`438`)

.. _changelog-3.0.0b1:

v3.0.0b1 (2021-07-02)
---------------------

Added
~~~~~

* Add support for ``TransferClient.get_shared_endpoint_list`` (:pr:`434`)

Changed
~~~~~~~

* Passthrough parameters to SDK methods for query params and body params are no
  longer accepted as extra keyword arguments. Instead, they must be passed
  explicitly in a ``query_params``, ``body_params``, or ``additional_fields``
  dictionary, depending on the context (:pr:`433`)

* The interface for retry parameters has been simplified. ``RetryPolicy``
  objects have been merged into the transport object, and retry parameters like
  ``max_retries`` may now be supplied directly as ``transport_params``
  (:pr:`430`)

.. _changelog-3.0.0a4:

v3.0.0a4 (2021-06-28)
---------------------

Added
~~~~~

* Add ``BaseClient`` to the top-level exports of ``globus_sdk``, so it can now
  be accessed under the name ``globus_sdk.BaseClient``

Fixed
~~~~~

* Fix several paginators which were broken in ``3.0.0a3`` (:pr:`431`)

Documentation
~~~~~~~~~~~~~

* Autodocumentation of paginated methods (:pr:`432`)

.. _changelog-3.0.0a3:

v3.0.0a3 (2021-06-25)
---------------------

Changed
~~~~~~~

* Pagination has changed significantly. (:pr:`418`)

  * Methods which support pagination like ``TransferClient.endpoint_search`` no
    longer return an iterable ``PaginatedResource`` type. Instead, these client
    methods return ``GlobusHTTPResponse`` objects with a single page of results.

  * Paginated variants of these methods are available by renaming a call from
    ``client.<method>`` to ``client.paginated.<method>``. So, for example, a
    ``TransferClient`` now supports ``client.paginated.endpoint_search()``.
    The arguments to this function are the same as the original method.

  * ``client.paginated.<method>`` calls return ``Paginator`` objects, which
    support two types of iteration: by ``pages()`` and by ``items()``. To
    replicate the same behavior as SDK v1.x and v2.x ``PaginatedResource``
    types, use ``items()``, as in
    ``client.paginated.endpoint_search("query").items()``

.. _changelog-3.0.0a2:

v3.0.0a2 (2021-06-10)
---------------------

Added
~~~~~

* A new subpackage is available for public use,
  ``globus_sdk.tokenstorage`` (:pr:`405`)

* Add client for Globus Groups API, ``globus_sdk.GroupsClient``. Includes a
  dedicated error class, ``globus_sdk.GroupsAPIError``

Changed
~~~~~~~

* Refactor response classes (:pr:`425`)

.. _changelog-3.0.0a1:

v3.0.0a1 (2021-06-04)
---------------------

Removed
~~~~~~~

* Remove ``allowed_authorizer_types`` restriction from ``BaseClient`` (:pr:`407`)

* Remove ``auth_client=...`` parameter to
  ``OAuthTokenResponse.decode_id_token`` (:pr:`400`)

Added
~~~~~

* ``globus-sdk`` now provides PEP561 typing data (:pr:`420`)

* ``OAuthTokenResponse.decode_id_token`` can now be provided a JWK and openid
  configuration as parameters. ``AuthClient`` implements methods for fetching
  these data, so that they can be fetched and stored outside of this call.
  There is no automatic caching of these data. (:pr:`403`)

Changed
~~~~~~~

* The interface for ``GlobusAuthorizer`` now defines
  ``get_authorization_header`` instead of ``set_authorization_header``, and
  additional keyword arguments are not allowed (:pr:`422`)

* New Transport layer handles HTTP details, variable payload
  encodings, and automatic request retries (:pr:`417`)

* Instead of ``json_body=...`` and ``text_body=...``, use ``data=...``
  combined with ``encoding="json"``, ``encoding="form"``, or
  ``encoding="text"`` to format payload data. ``encoding="json"`` is the
  default when ``data`` is a dict.

* By default, requests are retried automatically on potentially transient
  error codes (e.g. ``http_status=500``) and network errors with exponential
  backoff

* ``globus_sdk.BaseClient`` and its subclasses define ``retry_policy``
  and ``transport_class`` class attributes which can be used to customize the
  retry behavior used

* The JWT dependency has been updated to ``pyjwt>=2,<3`` (:pr:`416`)

* The config files in ``~/.globus.cfg`` and ``/etc/globus.cfg`` are no longer
  used. Configuration can now be done via environment variables (:pr:`409`)

* ``BaseClient.app_name`` is a property with a custom setter, replacing
  ``set_app_name`` (:pr:`415`)

Documentation
~~~~~~~~~~~~~

* Update documentation site style and layout (:pr:`423`)

.. _changelog_version2:

.. _changelog-2.0.1:

v2.0.1 (2021-02-02)
-------------------

Python Support
~~~~~~~~~~~~~~

* Remove support for python2 (:pr:`396`, :pr:`397`, :pr:`398`)

.. note:: globus-sdk version 2.0.0 was yanked due to a release issue.
          Version 2.0.1 is the first 2.x version.

.. _changelog-1.11.0:

v1.11.0 (2021-01-29)
--------------------

Added
~~~~~

* Add support for task skipped errors via
  ``TransferClient.task_skipped_errors`` and
  ``TransferClient.endpoint_manager_task_skipped_errors`` (:pr:`393`)

Development
~~~~~~~~~~~

* Internal maintenance (:pr:`389`, :pr:`390`, :pr:`391`, :pr:`392`)

.. _changelog-1.10.0:

v1.10.0 (2020-12-18)
--------------------

Fixed
~~~~~

* Add support for pyinstaller installation of globus-sdk (:pr:`387`)

.. _changelog-1.9.1:

v1.9.1 (2020-08-27)
-------------------

Fixed
~~~~~

* Fix ``GlobusHTTPResponse`` to handle responses with no ``Content-Type`` header (:pr:`375`)

.. _changelog-1.9.0:

v1.9.0 (2020-03-05)
-------------------

Added
~~~~~

* Add ``globus_sdk.IdentityMap``, a mapping-like object for Auth ID lookups (:pr:`367`)

* Add ``external_checksum`` and ``checksum_algorithm`` to ``TransferData.add_item()`` named arguments (:pr:`365`)

Changed
~~~~~~~

* Don't append trailing slashes when no path is given to a low-level client method like ``get()`` (:pr:`364`)

Development
~~~~~~~~~~~

* Minor documentation and build improvements (:pr:`369`, :pr:`362`)

.. _changelog-1.8.0:

v1.8.0 (2019-07-11)
-------------------

Added
~~~~~

* Add a property to paginated results which shows if more results are available (:pr:`346`)

Fixed
~~~~~

* Fix ``RefreshTokenAuthorizer`` to handle a new ``refresh_token`` being sent back by Auth (:pr:`359`)

* Fix typo in endpoint_search log message (:pr:`355`)

* Fix Globus Web App activation links in docs (:pr:`356`)

Documentation
~~~~~~~~~~~~~

* Update docs to state that Globus SDK uses semver (:pr:`357`)

.. _changelog-1.7.1:

v1.7.1 (2019-02-21)
-------------------

Added
~~~~~

* Allow arbitrary keyword args to ``TransferData.add_item()`` and ``DeleteData.add_item()``, which passthrough to the item bodies (:pr:`339`)

Development
~~~~~~~~~~~

* Minor internal improvements (:pr:`342`, :pr:`343`)

.. _changelog-1.7.0:

v1.7.0 (2018-12-18)
-------------------

Added
~~~~~

* Add ``get_task`` and ``get_task_list`` to ``SearchClient`` (:pr:`335`, :pr:`336`)

Development
~~~~~~~~~~~

* Internal maintenance and testing improvements (:pr:`331`, :pr:`334`, :pr:`333`)

.. _changelog-1.6.1:

v1.6.1 (2018-10-30)
-------------------

Changed
~~~~~~~

* Replace egg distribution format with wheels (:pr:`314`)

Development
~~~~~~~~~~~

* Internal maintenance

.. _changelog-1.6.0:

v1.6.0 (2018-08-29)
-------------------

Python Support
~~~~~~~~~~~~~~

* Officially add support for python 3.7 (:pr:`300`)

Removed
~~~~~~~
Added
~~~~~

* RenewingAuthorizer and its subclasses now expose the check_expiration_time method (:pr:`309`)

* Allow parameters to be passed to customize the request body of ConfidentialAppAuthClient.oauth2_get_dependent_tokens (:pr:`308`)

* Add the patch() method to BaseClient and its subclasses, sending an HTTP PATCH request (:pr:`302`)

Changed
~~~~~~~

* Use sha256 hashes of tokens (instead of last 5 chars) in debug logging (:pr:`305`)

* Make pickling SDK objects safer (but still not officially supported!) (:pr:`284`)

* Malformed SDK usage may now raise GlobusSDKUsageError instead of ValueError. GlobusSDKUsageError inherits from ValueError (:pr:`281`)

Fixed
~~~~~

* Correct handling of environment="production" as an argument to client construction (:pr:`307`)

Documentation
~~~~~~~~~~~~~

* Numerous documentation improvements (:pr:`279`, :pr:`294`, :pr:`296`, :pr:`297`)

.. _changelog-1.5.0:

v1.5.0 (2018-02-09)
-------------------

Added
~~~~~

* Add support for retrieving a local Globus Connect Personal endpoint's UUID (:pr:`276`)

Fixed
~~~~~

* Fix bug in search client parameter handling (:pr:`274`)

.. _changelog-1.4.1:

v1.4.1 (2017-12-20)
-------------------

Added
~~~~~

* Support connection timeouts. Default timeout of 60 seconds (:pr:`264`)

Fixed
~~~~~

* Send ``Content-Type: application/json`` on requests with JSON request bodies (:pr:`266`)

.. _changelog-1.4.0:

v1.4.0 (2017-12-13)
-------------------

Added
~~~~~

* Access token response data by way of scope name (:pr:`261`)

* Add (beta) SearchClient class (:pr:`259`)

Changed
~~~~~~~

* Make ``cryptography`` a strict requirement, globus-sdk[jwt] is no longer necessary (:pr:`257`, :pr:`260`)

* Simplify OAuthTokenResponse.decode_id_token to not require the client as an argument (:pr:`255`)

.. _changelog-1.3.0:

v1.3.0 (2017-11-20)
-------------------

Python Support
~~~~~~~~~~~~~~

* Improve error message when installation onto python2.6 is attempted (:pr:`245`)

Changed
~~~~~~~

* Raise errors on client instantiation when ``GLOBUS_SDK_ENVIRONMENT`` appears to be invalid, support ``GLOBUS_SDK_ENVIRONMENT=preview`` (:pr:`247`)

.. _changelog-1.2.2:

v1.2.2 (2017-11-01)
-------------------

Added
~~~~~

* Allow client classes to accept ``base_url`` as an argument to ``_init__()`` (:pr:`241`)

Changed
~~~~~~~

* Improve docs on ``TransferClient`` helper classes (:pr:`231`, :pr:`233`)

Fixed
~~~~~

* Fix packaging to not include testsuite (:pr:`232`)

.. _changelog-1.2.1:

v1.2.1 (2017-09-29)
-------------------

Changed
~~~~~~~

* Use PyJWT instead of python-jose for JWT support (:pr:`227`)

.. _changelog-1.2.0:

v1.2.0 (2017-08-18)
-------------------

Added
~~~~~

* Add Transfer symlink support (:pr:`218`)

Fixed
~~~~~

* Better handle UTF-8 inputs (:pr:`208`)

* Fix endpoint manager resume (:pr:`224`)

Documentation
~~~~~~~~~~~~~

* Doc Updates & Minor Improvements

.. _changelog-1.1.1:

v1.1.1 (2017-05-19)
-------------------

Fixed
~~~~~

* Use correct paging style when making ``endpoint_manager_task_list`` calls (:pr:`210`)

.. _changelog-1.1.0:

v1.1.0 (2017-05-01)
-------------------

Python Support
~~~~~~~~~~~~~~

* Add python 3.6 to supported platforms (:pr:`180`)

Added
~~~~~

* Add endpoint_manager methods to TransferClient (:pr:`191`, :pr:`199`, :pr:`200`, :pr:`201`, :pr:`203`)

* Support iterable requested_scopes everywhere (:pr:`185`)

Changed
~~~~~~~

* Change "identities_set" to "identity_set" for token introspection (:pr:`163`)

* Update dev status classifier to 5, prod (:pr:`178`)

Documentation
~~~~~~~~~~~~~

* Fix docs references to ``oauth2_start_flow_*`` (:pr:`190`)

* Remove "Beta" from docs (:pr:`179`)

Development
~~~~~~~~~~~

* Numerous improvements to testsuite

.. _changelog-1.0.0:

v1.0.0 (2017-04-10)
-------------------

Added
~~~~~

* Adds ``AuthAPIError`` with more flexible error payload handling (:pr:`175`)

.. _changelog-0.7.2:

v0.7.2 (2017-04-05)
-------------------

Added
~~~~~

* Add ``AuthClient.validate_token`` (:pr:`172`)

Fixed
~~~~~

* Bugfix for ``on_refresh`` users of ``RefreshTokenAuthorizer`` and ``ClientCredentialsAuthorizer`` (:pr:`173`)

.. _changelog-0.7.1:

v0.7.1 (2017-04-03)
-------------------

Removed
~~~~~~~

* Remove deprecated ``oauth2_start_flow_*`` methods (:pr:`170`)

Added
~~~~~

* Add the ``ClientCredentialsAuthorizer`` (:pr:`164`)

* Add ``jwt`` extra install target. ``pip install "globus_sdk[jwt]"`` installs ``python-jose`` (:pr:`169`)

.. _changelog-0.7.0:

v0.7.0 (2017-03-30)
-------------------

Removed
~~~~~~~

* Remove all properties of ``OAuthTokenResponse`` other than ``by_resource_server`` (:pr:`162`)

Fixed
~~~~~

* Make ``OAuthTokenResponse.decode_id_token()`` respect ``ssl_verify=no`` configuration (:pr:`161`)

.. _changelog-0.6.0:

v0.6.0 (2017-03-21)
-------------------

Added
~~~~~

* Add ``deadline`` support to ``TransferData`` and ``DeleteData`` (:pr:`159`)

Changed
~~~~~~~

* Opt out of the Globus Auth behavior where a ``GET`` of an identity username will provision that identity (:pr:`145`)

* Wrap some ``requests`` network-related errors in custom exceptions (:pr:`155`)

Fixed
~~~~~

* Fixup OAuth2 PKCE to be spec-compliant (:pr:`154`)

.. _changelog-0.5.1:

v0.5.1 (2017-02-25)
-------------------

Added
~~~~~

* Add support for the ``prefill_named_grant`` option to the Native App authorization flow (:pr:`143`)

Changed
~~~~~~~

* Unicode string improvements (:pr:`129`)

* Better handle unexpected error payloads (:pr:`135`)
