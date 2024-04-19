Globus Auth
===========

.. currentmodule:: globus_sdk

There are several types of client object for communicating with the Globus Auth
service. A client object may represent your application (as the driver of
authentication and authorization flows), in which case the
:class:`NativeAppAuthClient` or :class:`ConfidentialAppAuthClient` classes should
generally be used.

Client Classes
--------------

.. autoclass:: AuthClient
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: AuthLoginClient
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: NativeAppAuthClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

.. autoclass:: ConfidentialAppAuthClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

The :class:`IdentityMap` is a specialized object which aids in the particular
use-case in which the Globus Auth :meth:`AuthClient.get_identities` API is being used to
resolve large numbers of usernames or IDs. It combines caching, request
batching, and other functionality.

..
    We set special-members so that __getitem__ and __delitem__ are included.
    But then we need to exclude specific members because we don't want people
    reading about __weakref__ in our docs.
.. autoclass:: IdentityMap
   :members:
   :special-members:
   :exclude-members: __dict__,__weakref__
   :show-inheritance:

.. autoclass:: DependentScopeSpec

Auth Responses
--------------

.. autoclass:: OAuthTokenResponse
   :members:
   :show-inheritance:

.. autoclass:: OAuthDependentTokenResponse
   :members:
   :show-inheritance:

.. autoclass:: GetConsentsResponse
   :members:
   :show-inheritance:

.. autoclass:: GetIdentitiesResponse
   :members:
   :show-inheritance:

Errors
------

.. autoexception:: AuthAPIError

OAuth2 Flow Managers
--------------------

These objects represent in-progress OAuth2 authentication flows.
Most typically, you should not use these objects directly, but rather rely on the
:class:`NativeAppAuthClient` or :class:`ConfidentialAppAuthClient` objects
to manage these for you through their ``oauth2_*`` methods.

All Flow Managers inherit from the
:class:`GlobusOAuthFlowManager \
<.GlobusOAuthFlowManager>` abstract class.
They are a combination of a store for OAuth2 parameters specific to the
authentication method you are using and methods which act upon those parameters.

.. autoclass:: globus_sdk.services.auth.GlobusNativeAppFlowManager
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.services.auth.GlobusAuthorizationCodeFlowManager
   :members:
   :show-inheritance:

Abstract Flow Manager
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: globus_sdk.services.auth.flow_managers.GlobusOAuthFlowManager
   :members:
   :show-inheritance:
