Welcome to ``globus_sdk._testing``
==================================

.. warning::

    Use at your own risk! This subpackage is highly experimental. It may
    feature breaking changes to the data and the interfaces without prior
    notice.

This is an experimental internal module offered by the Globus SDK to share
API fixtures for use with the ``responses`` library.

Dependencies
------------

This toolchain requires the ``responses`` library.

``globus_sdk._testing`` is tested to operate with ``responses==0.17.0`` on
python3.6, and the latest version of ``responses`` on python3.7+ .

Recommended Fixtures
--------------------

Under pytest, this is the recommended fixture for setting up responses and
guaranteeing that requests are sent to the production hostnames:

.. code-block:: python

    @pytest.fixture(autouse=True)
    def mocked_responses(monkeypatch):
        responses.start()
        monkeypatch.setitem(os.environ, "GLOBUS_SDK_ENVIRONMENT", "production")
        yield
        responses.stop()
        responses.reset()

Methods and Classes
-------------------

Users of ``globus_sdk._testing`` have the following methods and classes
available:

``get_last_request``
    Get the last request which was received, or None if there were no requests.

``ResponseSet``
    A collection of mock responses, potentially all meant to be activated together
    (``.activate_all()``), or to be individually selected as options/alternatives
    (``.activate("case_foo")``).

``RegisteredResponse``
    A mock response along with descriptive metadata to let a fixture "pass data
    forward" to the consuming test cases. (e.g. a ``GET Task`` fixture which
    shares the ``task_id`` it uses with consumers via ``.metadata["task_id"]``)

``ResponseList``
    A series of mock responses which *must* be activated together in a single
    step. This can be stored in a ``ResponseSet`` as a case, describing a set
    of responses registered to a specific name.

``load_response_set``
    Optionally lookup a response set and activate all of its responses. If
    passed a ``ResponseSet``, activate it, otherwise the first argument is an
    ID used for lookup.

``load_response``
    Optionally lookup and activate an individual response. If given a
    ``RegisteredResponse``, activate it, otherwise the first argument is an ID
    of a ``ResponseSet`` used for lookup. By default, looks for the response
    registered under ``case="default"``.

``get_response_set``
    Lookup a ``ResponseSet`` as in ``load_response_set``, but without
    activating it.

``register_response_set``
    Register a new ``ResponseSet`` object.

Usage
-----

Activating Individual Responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once ``responses`` has been activated, each response fixture can be loaded and
activated by name:

.. code-block:: python

    from globus_sdk._testing import load_response

    # load_response will add the response to `responses` and return it
    load_response("auth.get_identities")
    # "case" is used to have a single name map to multiple responses
    data = load_response("auth.get_identities", case="multiple")

Responses can also be activated by passing an SDK client method, bound or
unbound, as in:

.. code-block:: python

    import globus_sdk
    from globus_sdk._testing import load_response

    load_response(globus_sdk.AuthClient.get_identities)
    load_response(globus_sdk.AuthClient.get_identities, case="unauthorized")

    # or, with a bound method
    ac = globus_sdk.AuthClient()
    load_response(ac.get_identities, case="multiple")

Activating "Scenarios"
~~~~~~~~~~~~~~~~~~~~~~

Some sets of fixtures may describe a scenario, and therefore it's desirable to
load all of them at once:

.. code-block:: python

    from globus_sdk._testing import load_response_set

    fixtures = load_response_set("scenario.foo")

Getting Responses and ResponseSets without Activating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to fetch a ``ResponseSet`` or ``RegisteredResponse`` without
activating it, you can do this via the ``get_response_set`` method. Responses
must always be part of a response set, and the default name for an individual
response is ``"default"``.

.. code-block:: python

    from globus_sdk import AuthClient
    from globus_sdk._testing import get_response_set

    # rset will not be activated
    rset = get_response_set(AuthClient.get_identities)
    # you can get an individual response from rset
    get_ids = rset.get("default")
    # you can manually activate a whole set
    rset.activate_all()
    # or just one response from it by name
    rset.activate("default")

Note that activating a whole repsonse set may or may not make sense. For
example, the response set for ``AuthClient.get_identities`` provides various
responses for the same API call.

Registering Response Sets
~~~~~~~~~~~~~~~~~~~~~~~~~

You can register your own response sets dynamically, and then load them up with
the same ``load_response_set`` method. Note that custom response sets will
override the builtin response sets, if names match.

.. code-block:: python

    from globus_sdk._testing import load_response_set, register_response_set
    import uuid

    # register a scenario under which Globus Auth get_identities and Globus
    # Transfer operation_ls both return payloads of `{"foo": "bar"}`
    # use an autogenerated endpoint ID and put it into the response metadata
    # register_response_set takes dict data and converts it to fixtures
    endpoint_id = str(uuid.uuid1())
    register_response_set(
        "foobar",
        {
            "get_identities": {
                "service": "auth",
                "path": "/v2/api/identities",
                "json": {"foo": "bar"},
            },
            "operation_ls": {
                "service": "transfer",
                "path": f"/operation/endpoint/{endpoint_id}/ls",
                "json": {"foo": "bar"},
            },
        },
        metadata={
            "endpoint_id": endpoint_id,
        },
    )

    # activate the result, and get it as a ResponseSet
    fixtures = load_response_set("foobar")
    # you can then pull the epid from the metadata
    epid = fixtures.metadata["endpoint_id"]
    transfer_client.operation_ls(epid)

``register_response_set`` can therefore be used to load fixture data early in
a tetstsuite run (e.g. as an autouse session-level fixture), for reference
later in the testsuite.

Loading Responses without Registering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because ``RegisteredResponse`` takes care of resolving ``"auth"`` to the Auth
URL, ``"transfer"`` to the Transfer URL, and so forth, you might want to use
``globus_sdk._testing`` in lieu of ``responses`` even when registering single
responses for individual tests.

To support this mode of usage, ``load_response`` can take a
``RegisteredResponse`` instance, and ``load_response_set`` can take a
``ResponseSet`` instance.

Consider the following example of a parametrized test which uses
``load_response(RegisteredResponse(...))`` as a replacement for
``responses.add``:

.. code-block:: python

    from globus_sdk._testing import load_response, RegisteredResponse
    import pytest


    @pytest.mark.parametrize("message", ["foo", "bar"])
    def test_get_identities_sends_back_strange_message(message):
        load_response(
            RegisteredResponse(
                service="auth",
                path="/v2/api/identities",
                json={"message": message},
            )
        )

        ac = globus_sdk.AuthClient()
        res = ac.get_identities(usernames="foo@example.com")
        assert res["message"] == message


In this mode of usage, the response set registry is skipped altogether. It is
not necessary to name or organize the response fixtures in a way that is usable
outside of the specific test.

Using non-default responses.RequestsMock objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, all methods in ``globus_sdk._testing`` which converse with
``responses`` use the default mock. This is the behavior offered by
``responses.add(...)`` and similar methods.

However, you can pass a custom ``RequestsMock`` if so desired to the following
methods:

* ``get_last_request``
* ``load_response_set``
* ``load_response``

as a keyword argument, ``requests_mock``.
e.g.


.. code-block:: python

    from globus_sdk._testing import get_last_request
    import responses

    custom_mock = responses.RequestsMock(...)
    ...

    get_last_request(requests_mock=custom_mock)
