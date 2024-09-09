.. _globus_authorizers:

Globus Authorizers
==================

.. currentmodule:: globus_sdk.authorizers

Globus SDK clients need credentials (tokens) to authenticate against services
and authorize their various API calls. Using Globus Auth, the Globus OAuth2
service, clients can be provided with credentials which are either static or
dynamic.

The interface used to handle these credentials is :class:`GlobusAuthorizer`.
:class:`GlobusAuthorizer` defines methods which provide an ``Authorization``
header for HTTP requests, and different implementations handle Refresh Tokens,
Access Tokens, Client Credentials, and their various usage modes.

A :class:`GlobusAuthorizer` is an object which defines the following two
operations:

- get an ``Authorization`` header
- handle a 401 Unauthorized error

Clients contain authorizers, and use them to get and refresh their credentials.
Whenever using the :ref:`Service Clients <services>`, you should be passing in an
authorizer when you create a new client unless otherwise specified.

The type of authorizer you will use depends very much on your application, but
if you want examples you should look at the :ref:`examples section
<examples-authorization>`.
It may help to start with the examples and come back to the reference
documentation afterwards.

The Authorizer Interface
------------------------

We define the interface for ``GlobusAuthorizer`` objects in terms of an
Abstract Base Class:

.. autoclass:: GlobusAuthorizer
    :members:
    :member-order: bysource

Authorizers within this SDK fall into two categories:

 * "Static Authorizers" already contain all authorization data and simply format it
   into the proper authorization header.
   These all inherit from the ``StaticGlobusAuthorizer`` class.

 * "Renewing Authorizer" take some initial parameters but internally define a
   functional behavior to acquire new authorization data as necessary.
   These all inherit from the ``RenewingGlobusAuthorizer`` class.

.. autoclass:: StaticGlobusAuthorizer
    :member-order: bysource
    :show-inheritance:

.. autoclass:: RenewingAuthorizer
    :member-order: bysource
    :show-inheritance:

Authorizer Types
----------------

.. currentmodule:: globus_sdk

All of these types of authorizers can be imported from
``globus_sdk.authorizers``.

.. autoclass:: AccessTokenAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: RefreshTokenAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: ClientCredentialsAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: BasicAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: NullAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:
