.. _userguide_understanding_service_accounts:

Understanding Service Accounts
==============================

Some clients registered in Globus may operate as independent "service accounts",
distinct actors with their own identities.
These are also referred to as "client identities" because the actor in question
is the client itself.
Service accounts are useful for a wide range of automation tasks, in which users
want to leverage Globus APIs, but without handling login flows and user
credentials.

Service Accounts are Clients
----------------------------

To create a service account, users must register a new Globus Auth client as
a Service Account, capable of performing a *client credentials grant* to get
its tokens.
Once it is so registered, such a client will have an ID and secret, which can be
passed into interfaces in the SDK.

The client credentials (ID and secret) are used to get tokens to power
interactions with Globus APIs, and SDK's :class:`globus_sdk.GlobusApp` and
:class:`globus_sdk.ClientCredentialsAuthorizer` will automatically cache and
reload these tokens appropriately.

.. note::

    In order to be used as a Service Account, a client must have an ID and secret.
    However, not every client with an ID and secret supports this usage! Clients
    may be registered with various different OAuth2 grant types enabled, and some
    clients have an ID and secret but are used to authenticate user logins!

    Put another way: having client credentials is *necessary but not sufficient*
    for this kind of usage.


Disambiguation: "Clients" vs "Client Identities" vs "Service Accounts"
----------------------------------------------------------------------

There are two different meanings for the word "client", from different domains.

Conventionally, a library's adapter for a web API is a "client".
In the SDK, we primarily use the word "client" to refer to these API connectors,
as in ``TransferClient``, ``GroupsClient``, etc.

OAuth2 calls an application registered with the service a "client".
A "Client Identity" is a Globus Auth concept which uses this meaning of
"client".

As a result of this ambiguity, this documentation will prefer to refer to
"Client Identities" as "Service Accounts", which is the term which is used in
other Globus documentation and the web interface.


Service Account Permissions
---------------------------

Service Accounts have their own assigned identities, group memberships, and
permissions within Globus.
They are not implicitly linked in any way to the user who created them, or the
administrators who manage them.
Their permissions are isolated.

Users of Service Accounts need to separately assign permissions to these
identities, depending on what resources the client is meant to access.


Policies Which Conflict With Service Accounts
---------------------------------------------

A number of the configurable policies on Globus resources conflict with use of
Service Accounts.
Users often find that they cannot substitute Service Accounts for their own
credentials without also adapting their workflows or configurations to support
this usage.

In particular, users should be aware of the following classes of issues, and
potential workarounds.

Identity-specific Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because clients are not associated with their owners, identity-specific
permissions for users can't be directly "shared" with their clients.

If your account has permissions to access a resource, but you wish to use a
Service Account to interact with it, add a second permission to give the Service
Account access as well.

Domain Requirements
~~~~~~~~~~~~~~~~~~~

Resources may apply policies which require a specific domain for users.
For example, a University of Chicago Collection may require ``uchicago.edu``
usernames.

Service Accounts have a fixed domain of ``clients.auth.globus.org`` and
therefore cannot satisfy these requirements.

Use user-specific access policies or permissions delegation features, like Guest
Collections, to allow Service Accounts to specifically access resources.

Session Timeouts
~~~~~~~~~~~~~~~~

Globus resources may configure authentication timeouts, forcing users to
reauthenticate within a fixed time window to use a resource.
This is done by checking the Globus Auth session associated with the user's
tokens for last authentication times.

For example, a Collection may require that users have logged in within the last
hour to access data -- this is part of the suite of features for High Assurance
data access.

A Service Account authenticates each time it fetches a token, but does not have
a Globus Auth session associated with those authentications. (There is no
browser session interaction in such cases.)
As such, a Service Account cannot satisfy these policies under a naive
interpretation.

Globus Connect Server implements a special rule to handle this case: session
timeouts are never enforced on Service Accounts.
Other services may implement similar policies or require that access to Service
Accounts be configured separately from regular user permissions.
