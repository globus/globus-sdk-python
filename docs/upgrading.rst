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

The signatures for these two data constructors has changed to remove support
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
``TransferClient.get_submsission_id()``, as in:

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
    "``globus_sdk.experimental.scope_parser``", "``globus_sdk.scopes``"

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
