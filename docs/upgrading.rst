.. _upgrading:

Upgrading
=========

This guide covers upgrading and migration between Globus SDK versions.
It is meant to help explain and resolve incompatibilities and breaking
changes, and does not cover all new features.

When upgrading, you should also read the relevant section of the
:ref:`changelog`.
The changelog can also be a source of information about new features
between major releases.

Many explanations are written in terms of ``TransferClient`` for consistency,
but apply to all client classes, including ``AuthClient``,
``NativeAppAuthClient``, ``ConfidentialAppAuthClient``, ``SearchClient``, and
``GroupsClient``.

Version Parsing
---------------

In the event that a codebase must support multiple versions of
the globus-sdk at the same time, consider adding this snippet:

.. code-block:: python

    import importlib.metadata

    GLOBUS_SDK_VERSION = importlib.metadata.distribution("globus_sdk").version
    GLOBUS_SDK_MAJOR_VERSION = int(GLOBUS_SDK_VERSION.split(".")[0])

This will parse the Globus SDK version information into a tuple and grab the
first element (the major version number) as an integer.

Then, code can dispatch with

.. code-block:: python

    if GLOBUS_SDK_MAJOR_VERSION < 3:
        pass  # do one thing
    else:
        pass  # do another

From 3.x to 4.0
---------------

``TransferData`` and ``DeleteData`` Do Not Take a ``TransferClient``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The signatures for these two data constructors have changed to remove support
for ``transfer_client`` as their first parameter.

Generally, update usage which passed a client to omit it:

.. code-block:: python

    from globus_sdk import TransferClient, TransferData, DeleteData

    # globus-sdk v3

    tc = TransferClient(...)
    tdata = TransferData(tc, SRC_COLLECTION, DST_COLLECTION)
    tc.submit_transfer(tdata)

    tc = TransferClient(...)
    ddata = DeleteData(tc, COLLECTION)
    tc.submit_delete(tdata)

    # globus-sdk v4

    tdata = TransferData(SRC_COLLECTION, DST_COLLECTION)
    tc = TransferClient(...)
    tc.submit_transfer(tdata)

    ddata = DeleteData(COLLECTION)
    tc = TransferClient(...)
    tc.submit_delete(tdata)

Users who are using keyword arguments to pass collection IDs without a
``transfer_client`` do not need to make any change. For example:

.. code-block:: python

    from globus_sdk import TransferData, DeleteData

    # globus-sdk v3 or v4

    tdata = TransferData(
        source_endpoint=SRC_COLLECTION, destination_endpoint=DST_COLLECTION
    )
    ddata = DeleteData(endpoint=COLLECTION)

The client object was used to fetch a ``submission_id`` on initialization.
Users typically will rely on ``TransferClient.submit_transfer()`` and
``TransferClient.submit_delete()`` filling in this value.
To control when a submission ID is fetched, use
``TransferClient.get_submission_id()``, as in:

.. code-block:: python

    from globus_sdk import TransferClient, TransferData

    # globus-sdk v3 or v4

    tc = TransferClient(...)
    submission_id = tc.get_submission_id()["value"]

    tdata = TransferData(
        source_endpoint=SRC_COLLECTION,
        destination_endpoint=DST_COLLECTION,
        submission_id=submission_id,
    )


``ConfidentialAppAuthClient`` Cannot Directly Call ``get_identities``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users of client identities are now required to get tokens in order to use the
Get Identities API, and will need to use the ``AuthClient`` class for this
purpose.
This can most simply be managed by use of a ``ClientApp`` to automatically
fetch the appropriate tokens.

Update usage like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk import ConfidentialAppAuthClient

    client = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)

    identities = client.get_identities(usernames="globus@globus.org")

    # globus-sdk v4
    from globus_sdk import ClientApp, AuthClient

    app = ClientApp(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    client = AuthClient(app=app)

    identities = client.get_identities(usernames="globus@globus.org")


Scope Constants Are Now Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Under version 3, many scopes were provided as string constants.
For example, ``globus_sdk.TransferClient.scopes.all`` was a string.

In version 4, these constants are now :class:`Scope <globus_sdk.scopes.Scope>`
objects. They can be rendered to strings using ``str()`` and no longer need to
be converted to :class:`Scope <globus_sdk.scopes.Scope>`\s in order to use
methods.

Convert usage which stringifies scopes like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import AuthScopes

    my_scope_str: str = AuthScopes.openid

    # globus-sdk v4
    from globus_sdk.scopes import AuthScopes

    my_scope_str: str = str(AuthScopes.openid)

And convert usage which builds scope objects like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import AuthScopes, Scope

    my_scope: Scope = Scope(AuthScopes.openid)

    # globus-sdk v4
    from globus_sdk.scopes import AuthScopes, Scope

    my_scope: Scope = AuthScopes.openid

``ScopeBuilder``\s are now ``ScopeCollection``\s
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As part of the refactor of scope constants, the objects which were previously
called "scope builders" are now "scope collections".
Scope collections may be static or dynamic, depending on whether or not they
statically provide their scopes at the class level or dynamically compute scopes
as instance attributes.

The following entities are therefore renamed in addition to having changes to
their implementations:

..  csv-table::
    :header: "Old name", "New name"

    "``GCSEndpointScopeBuilder``", "``GCSEndpointScopes``"
    "``GCSCollectionScopeBuilder``", "``GCSCollectionScopes``"
    "``SpecificFlowScopeBuilder``", "``SpecificFlowScopes``"

Scope collections provide ``Scope`` objects, not strings.
Therefore, update code like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import Scope, SpecificFlowScopeBuilder

    my_flow_scope = Scope(SpecificFlowScopeBuilder(FLOW_ID).user)

    # globus-sdk v4
    from globus_sdk.scopes import SpecificFlowScopes

    my_flow_scope = SpecificFlowScopes(FLOW_ID).user

Scopes Are Immutable and Have New Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`Scope <globus_sdk.scopes.Scope>` object in v3 of the SDK could be
updated with in-place modifications.
In v4, these objects are now frozen, and their methods have been altered to
suit their immutability.

In particular, ``add_dependency`` has been replaced with ``with_dependency``,
which builds and returns a new scope rather than making changes to an existing
value.

Update ``add_dependency`` usage like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import Scope

    my_scope = Scope(ROOT_SCOPE_STRING)
    my_scope.add_dependency(DEPENCENCY_STRING)

    # globus-sdk v4
    from globus_sdk.scopes import Scope

    my_scope = Scope(ROOT_SCOPE_STRING)
    my_scope = my_scope.with_dependency(DEPENCENCY_STRING)

For optional dependencies, the ``optional`` parameter must now be specified when
creating the dependency scope, not when adding it:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import Scope

    my_scope = Scope(ROOT_SCOPE_STRING)
    my_scope.add_dependency(DEPENDENCY_STRING, optional=True)

    # globus-sdk v4
    from globus_sdk.scopes import Scope

    my_scope = Scope(ROOT_SCOPE_STRING)
    dependency = Scope(DEPENDENCY_STRING, optional=True)
    my_scope = my_scope.with_dependency(dependency)

ScopeParser Is Now Separate from Scope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scope parsing has been split from ``Scope`` to a new class, ``ScopeParser``.
Additionally, ``Scope.serialize`` and ``Scope.deserialize`` have been removed,
and ``Scope.parse`` is now a wrapper over ``ScopeParser.parse`` which always
builds and returns one scope.

Users who need to parse multiple scopes should rely on ``ScopeParser.parse``.
For example, update like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import Scope

    my_scopes: list[Scope] = Scope.parse(scope_string)

    # globus-sdk v4
    from globus_sdk.scopes import Scope, ScopeParser

    my_scopes: list[Scope] = ScopeParser.parse(scope_string)

Scope Collections Provide ``__iter__``, not ``__str__``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 3, the SDK scope collection objects provided a pretty printer in the
form of ``str()``. Users could call ``str(TransferClient.scopes)`` to see the
available scopes.

In version 4, this has been removed, but the collection types provide
``__iter__`` over their member scopes instead. Therefore, you can fetch all
scopes for the Globus Transfer service via ``list(TransferClient.scopes)`` or
similar usage.

Token Storage Subpackage Renamed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The subpackage providing token storage components has been renamed and slightly
restructured.

The package name is changed from
``globus_sdk.tokenstorage`` to ``globus_sdk.token_storage``.

Furthermore, the legacy :ref:`storage adapters <storage_adapters>` are now only
available from ``globus_sdk.token_storage.legacy``.

Therefore, usages of the modern :ref:`token storage interface <token_storages>`
should update like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.tokenstorage import JSONTokenStorage

    # globus-sdk v4
    from globus_sdk.token_storage import JSONTokenStorage

For legacy adapter usage, update like so:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.tokenstorage import SimpleJSONFileAdapter

    # globus-sdk v4
    from globus_sdk.token_storage.legacy import SimpleJSONFileAdapter

.. note::

    The ``legacy`` interface is soft-deprecated.
    In version 4.0.0 it will not emit deprecation warnings.
    Future SDK versions will eventually deprecate and remove these interfaces.

Deprecated Timers Aliases Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the version 3 lifecycle, the ``TimersClient`` and ``TimersAPIError``
classes were renamed. Their original names, ``TimerClient`` and
``TimerAPIError`` were retained as compatibility aliases.

These have been removed. Use ``TimersClient`` and ``TimersAPIError``.

Deprecated Experimental Aliases Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the version 3 lifecycle, several modules were added under
``globus_sdk.experimental`` and later promoted to new names in the main
``globus_sdk`` namespace.
Compatibility aliases were left in place.

Under version 4, the compatibility aliases have been removed.
The removed alias and new module names are shown in the table below.

..  csv-table::
    :header: "Removed alias", "New name"

    "``globus_sdk.experimental.auth_requirements_error``", "``globus_sdk.gare``"
    "``globus_sdk.experimental.globus_app``", "``globus_sdk.globus_app``"
    "``globus_sdk.experimental.scope_parser``", "``globus_sdk.scopes``"
    "``globus_sdk.experimental.consents``", "``globus_sdk.scopes.consents``"
    "``globus_sdk.experimental.tokenstorage``", "``globus_sdk.token_storage``"
    "``globus_sdk.experimental.login_flow_manager``", "``globus_sdk.login_flows``"

``SearchQuery`` is Removed, use ``SearchQueryV1`` Instead
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``SearchQuery`` helper was removed in version 4 in favor of the
:class:`SearchQueryV1 <globus_sdk.SearchQueryV1>` type.

Simply replace one type with the other for most simple usages:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk import SearchQuery

    query = SearchQuery(q="foo")

    # globus-sdk v4
    from globus_sdk import SearchQuery

    query = SearchQueryV1(q="foo")

Note that ``SearchQuery`` supported the query string, ``q``, as a positional
argument, but ``SearchQueryV1`` requires that it is passed as a named
parameter.

``SearchQuery`` also supported helper methods which are not provided by
``SearchQueryV1``.
These must be replaced by setting the relevant parameters directly or on
initialization.
For example:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk import SearchQuery

    query = SearchQuery(q="foo")
    query.set_offset(100)  # removed in v4

    # globus-sdk v4
    from globus_sdk import SearchQuery

    query = SearchQueryV1(q="foo", offset=100)  # on init
    # or
    query = SearchQueryV1(q="foo")
    query["offset"] = 100  # by setting a field

.. note::

    :class:`SearchQueryV1 <globus_sdk.SearchQueryV1>` was added in
    ``globus-sdk`` version 3, so this transition can be made prior to upgrading
    to version 4.

``SearchClient.create_entry`` and ``SearchClient.update_entry`` Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These methods were deprecated in version 3 in favor of ``SearchClient.ingest``,
which provides greater functionality and a more uniform interface.

For any document being passed by these methods, upgrade to using an ingest
document with ``"ingest_type": "GMetaEntry"``.
Consult the :extdoclink:`Search Ingest Guide </search/ingest/>`
for details on the document formats.

``MutableScope`` is Removed, use ``Scope`` Instead
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``MutableScope`` type was removed in version 4 in favor of the
:class:`Scope <globus_sdk.scopes.Scope>` type.
When manipulating scopes as objects, use
:class:`Scope <globus_sdk.scopes.Scope>` anywhere that
``MutableScope`` was used, for example:

.. code-block:: python

    # globus-sdk v3
    from globus_sdk.scopes import MutableScope

    my_scope = MutableScope("urn:globus:auth:scopes:transfer.api.globus.org:all")

    # globus-sdk v4
    from globus_sdk.scopes import Scope

    my_scope = Scope("urn:globus:auth:scopes:transfer.api.globus.org:all")

.. note::

    The :class:`Scope <globus_sdk.scopes.Scope>` type was added in Globus SDK
    v3, so this transition can be made prior to upgrading to version 4.

``requested_scopes`` is Required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several methods have historically taken an optional parameter,
``requested_scopes``.

- ``ConfidentialAppAuthClient.oauth2_client_credentials_tokens``
- ``ConfidentialAppAuthClient.oauth2_start_flow``
- ``NativeAppAuthClient.oauth2_start_flow``

In previous versions of the SDK, these methods provided a default value for
``requested_scopes`` of
``"openid profile email urn:globus:auth:scopes:transfer.api.globus.org:all"``.
This default has now been removed and users should always specify the scopes
they need when using these methods.

Users of ``GlobusApp`` constructs (``UserApp`` and ``ClientApp``) do not need
to update their usage.

The default could only be used by applications which only use Globus Transfer
and Globus Auth.
Change:

.. code-block:: python

    # globus-sdk v3
    auth_client.oauth2_start_flow()
    authorize_url = auth_client.oauth2_get_authorize_url()

    # globus-sdk v4
    auth_client.oauth2_start_flow(requested_scopes=globus_sdk.TransferClient.scopes.all)
    authorize_url = auth_client.oauth2_get_authorize_url()

Customizing the Transport Has Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 3, SDK users could customize the ``RequestsTransport`` object
contained within a client in two ways.
One was to customize a client class by setting the ``transport_class`` class
attribute, and the other was to pass ``transport_params`` to the client
initializer.

In version 4, these mechanisms have been replaced with support for passing a
``RequestsTransport`` object directly to the initializer.

For users who are customizing the parameters to the transport class, they
should now explicitly instantiate the transport object:

.. code-block:: python

    # globus-sdk v3
    import globus_sdk

    client = globus_sdk.GroupsClient(transport_params={"http_timeout": 120.0})

    # globus-sdk v4
    import globus_sdk
    from globus_sdk.transport import RequestsTransport

    client = globus_sdk.GroupsClient(transport=RequestsTransport(http_timeout=120.0))

or use the ``tune()`` context manager:

.. code-block:: python

    # globus-sdk v4
    import globus_sdk

    client = globus_sdk.GroupsClient()
    with client.transport.tune(http_timeout=120.0):
        my_groups = client.get_my_groups()

Retry Check Configuration Moved to ``retry_config``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Globus SDK v3, a client's ``transport`` contained all of its retry
behaviors, including the checks which are run on each request, the
configuration of those checks, and the sleep and backoff behaviors.

Under v4, the configuration of checks has been split off into a separate
attribute of the client, ``retry_config``.

These changes primarily impact users who were using a custom
``RequestsTransport`` class, and should simplify their usage.

For example, in order to treat only 502s as retriable transient errors, users
previously had a custom transport type.
This could then be configured on a custom client class:

.. code-block:: python

    # globus-sdk v3
    import globus_sdk
    from globus_sdk.transport import RequestsTransport


    class MyTransport(RequestsTransport):
        TRANSIENT_ERROR_STATUS_CODES = (502,)


    class MyClientClass(globus_sdk.GroupsClient):
        transport_class = MyTransport


    client = MyClientClass()

Under SDK v4, in order to customize the same information, users can simply
create a client and then modify the attributes of the ``retry_config`` object:

.. code-block:: python

    # globus-sdk v4
    import globus_sdk

    client = globus_sdk.GroupsClient()
    client.retry_config.transient_error_status_codes = (502,)

Similar to the ``tune()`` context manager of ``RequestsTransport``, there is
also a ``tune()`` context manager for the retry configuration. ``tune()``
supports the ``max_sleep``, ``max_retries``, and ``backoff`` configurations,
which users of ``RequestsTransport.tune()`` may already recognize.
For example, users can suppress retries:

.. code-block:: python

    # globus-sdk v4
    import globus_sdk

    client = globus_sdk.GroupsClient()
    with client.retry_config.tune(max_retries=1):
        my_groups = client.get_my_groups()

A ``retry_config`` can also be passed to clients on initialization:

.. code-block:: python

    # globus-sdk v4
    import globus_sdk
    from globus_sdk.transport import RetryConfig

    client = globus_sdk.GroupsClient(retry_config=RetryConfig(max_retries=2))
    my_groups = client.get_my_groups()

Clients No Longer Define ``base_path``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 3 and earlier, client classes defined an attribute ``base_path``
which was joined as a prefix to request paths for the HTTP methods: ``get()``,
``put()``, ``post()``, ``patch()``, ``delete()``, ``head()``, and ``request()``.
The ``base_path`` attribute has been removed and direct use of HTTP APIs now
requires the full path when bare HTTP methods are used.

``base_path`` values were also used in the testing tools defined by
``globus_sdk.testing`` and have similarly been removed.

The ``base_path`` was automatically deduplicated when provided to SDK version 3,
meaning that code which includes this prefix will work on both SDK version 3 and
version 4.

For example, ``TransferClient`` defined a ``base_path`` of ``"v0.10"``.
As a result, the request URI for a ``get()`` HTTP call would be mapped as follows:

.. code-block:: python

    import globus_sdk

    tc = globus_sdk.TransferClient()

    # GET https://transfer.api.globus.org/v0.10/foo/bar
    tc.get("/foo/bar")

In version 4, without the ``base_path``, the mapping is as follows:

.. code-block:: python

    # GET https://transfer.api.globus.org/foo/bar
    tc.get("/foo/bar")

Due to the deduplication of a leading ``base_path`` in version 3, the following
snippet has the same effect in both versions:

.. code-block:: python

    # GET https://transfer.api.globus.org/v0.10/foo/bar
    tc.get("/v0.10/foo/bar")

Clients with a ``base_path`` and the values they defined in version 3 are listed
below.

==================  ===========
Client Class        base_path
==================  ===========
``TransferClient``  ``"v0.10"``
``GroupsClient``    ``"v2"``
==================  ===========


From 1.x or 2.x to 3.0
-----------------------

The :ref:`v3 changelog <changelog_version3>` covers the full list of changes
made in version 3 of the Globus SDK.

Because version 2 did not introduce any changes to the SDK code other than
supported python versions, you may also want to view this section when
upgrading from version 1.

Type Annotations
~~~~~~~~~~~~~~~~

The Globus SDK now provides PEP 561 type annotation data.

This means that codebases which use ``mypy`` or similar tools to check type
annotations may see new warnings or errors when using version 3 of the SDK.

.. note::

    If you believe an annotation in the SDK is incorrect, please visit our
    `issue tracker <https://github.com/globus/globus-sdk-python/issues>`_ to
    file a bug report!

Automatic Retries
~~~~~~~~~~~~~~~~~

Globus SDK client methods now automatically retry failing requests when
encountering network errors and certain classes of server errors (e.g. rate
limiting).

For most users, retry logic can be removed.
Change:

.. code-block:: python

    import globus_sdk

    # globus-sdk v1 or v2
    tc = globus_sdk.TransferClient(...)

    response = None
    count, max_retries = 0, 10
    while response is None and count < max_retries:
        count += 1
        try:  # any operation, just an example
            response = tc.get_endpoint(foo)
        except globus_sdk.NetworkError:
            pass

    # globus-sdk v3
    tc = globus_sdk.TransferClient(...)
    response = tc.get_endpoint(foo)  # again, just an example operation

Updates to BaseClient Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may be using the globus-sdk ``BaseClient`` object to implement a custom
client or for type annotations. Firstly, ``BaseClient`` is available from the
base ``globus_sdk`` namespace.

Change:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk.base import BaseClient

    # globus-sdk v3
    from globus_sdk import BaseClient

Secondly, creating a ``BaseClient`` is different. Previously, initializing a
``BaseClient`` had one required positional argument ``service``. Now, this
exists as a class attribute, which subclasses can overwrite.

Change:

.. code-block:: python

    # globus-sdk v1 or v2
    class MyClient(BaseClient):
        pass


    MyClient("my-service", **kwargs)


    # globus-sdk v3
    class MyClient(BaseClient):
        service_name = "my-service"


    MyClient(**kwargs)

Import exceptions from globus_sdk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several exceptions which were available in v2 under ``globus_sdk.exc`` are now
only available from the ``globus_sdk`` namespace.

Change:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk.exc import SearchAPIError, TransferAPIError, AuthAPIError

    # globus-sdk v3
    from globus_sdk import SearchAPIError, TransferAPIError, AuthAPIError

Note that this also may appear in your exception handling, as in:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk import exc

    try:
        ...
    except exc.TransferAPIError:  # by way of example, any error here
        ...

    # globus-sdk v3
    import globus_sdk

    try:
        ...
    except globus_sdk.TransferAPIError:
        ...

Low Level API for Passing Data is Improved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 2 of the SDK, passing data to client ``post()``, ``put()``, and
``patch()`` methods required the use of either ``json_body`` or ``text_body``.
Furthermore, ``text_body`` would (confusingly!) send a FORM body if it were
passed a dictionary.

Now, these behaviors are described by ``data`` (a body for these HTTP methods)
and ``encoding`` (an explicit data format parameter). If the ``encoding`` is
not set, the default behavior is that if ``data`` is a dictionary, it will be
sent as JSON. If ``data`` is a string, it will be sent as text.

``encoding`` can be set to ``"json"`` or ``"form"`` to explicitly format the
data.

Change code for a JSON PUT like so:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.put("/some/custom/path", json_body={"a": "dict", "of": "data"})

    # globus-sdk v3
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.put("/some/custom/path", data={"a": "dict", "of": "data"})

Or a FORM POST like so:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.post("/some/custom/path", text_body={"a": "dict", "of": "data"})

    # globus-sdk v3
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.put("/some/custom/path", data={"a": "dict", "of": "data"}, encoding="form")

Passthrough Parameters are Explicit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many methods in version 2 accepted arbitrary keyword arguments which were then
transformed into query or body parameters based on the context. This is no
longer allowed, but methods can still be passed additional query parameters in the
form of a ``query_params`` dict.

For example, if the Transfer API is known to support a query param ``foo=bar``
for ``GET Endpoint``, but the SDK does not include this parameter, the way that
it can be added to a request has changed as follows:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.get_endpoint(epid, foo="bar")

    # globus-sdk v3
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    tc.get_endpoint(epid, query_params={"foo": "bar"})

.. note::

    If a parameter which you need is not supported by the Globus SDK, use
    ``query_params`` to work around it! But also, feel free to visit our
    `issue tracker <https://github.com/globus/globus-sdk-python/issues>`_ to
    request an improvement.

Responses are always GlobusHTTPResponse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 2, ``GlobusHTTPResponse`` inherited from a base class,
``GlobusResponse``. In version 3, the distinction has been eliminated and
responses are only ``GlobusHTTPResponse``.

This may appear in contexts where you type annotate or use ``isinstance`` checks
to check the type of an object.

Change:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk.response import GlobusResponse

    data = some_complex_func()
    if isinstance(data, GlobusResponse):
        ...

    # globus-sdk v3
    from globus_sdk import GlobusHTTPResponse

    data = some_complex_func()
    if isinstance(data, GlobusHTTPResponse):
        ...

Pagination is now explicit
~~~~~~~~~~~~~~~~~~~~~~~~~~

In version 2, paginated methods of ``TransferClient`` returned a
``PaginatedResource`` iterable type.
In version 3, no methods return paginators by default, and pagination is always
opt-in. See also :ref:`doc on making paginated calls <making_paginated_calls>`.

Change:

.. code-block:: python

    # globus-sdk v1 or v2
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    for endpoint_info in tc.endpoint_search("query"):
        ...

    # globus-sdk v3
    from globus_sdk import TransferClient

    tc = TransferClient(...)
    for endpoint_info in tc.paginated.endpoint_search("query").items():
        ...

Authorizer Methods
~~~~~~~~~~~~~~~~~~

``GlobusAuthorizer`` objects have had their methods modified.

In particular, in version 2, authorizers have a method
``set_authorization_header`` for modifying a dict.

This has been replaced in version 3 with a method ``get_authorization_header``
which returns an ``Authorization`` header value.

Configuration has Changed
~~~~~~~~~~~~~~~~~~~~~~~~~

The Globus SDK no longer reads configuration data from ``/etc/globus.cfg`` or
``~/.globus.cfg``.

If you are using these files to customize the behavior of the SDK, see
:ref:`the configuration documentation <config>`.

Internal Changes to components including Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several modules and components which are considered mostly or entirely internal
have been reorganized.

In particular, if you are using undocumented methods from
``globus_sdk.config``, note that this has been largely rewritten.
(These are not considered public APIs.)


From 1.x to 2.0
---------------

Also see the :ref:`v2 changelog <changelog_version2>`.

When upgrading from version 1 to version 2 of the Globus SDK, no code changes
should be necessary.

Version 2 removed support for python2 but made no other changes.

Simply ensure that you are running python 3.6 or later and update version
specifications to ``globus_sdk>=2,<3``.
