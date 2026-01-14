.. _userguide_client_identities:

Using Client Identities
=======================

Some clients registered in Globus may operate as independent "service accounts",
distinct actors with their own identities.
This is useful for a wide range of automation tasks, in which users want to
leverage Globus APIs, but without handling login flows and user credentials.

To make use of Client Identities in this way, the client must be registered as a
"service account", capable of performing a *client credentials grant* to get
its tokens.
Once it is so registered, such a client will have an ID and secret, which can be
passed into interfaces in the SDK.
The client credentials (ID and secret) are used to get tokens to power
interactions with Globus APIs, and SDK's GlobusApp will automatically cache and reload
these tokens appropriately.

.. note::

    In order to be used as a Client Identity, a client must have an ID and secret.
    However, not every client with an ID and secret supports this usage! Clients
    may be registered with various different OAuth2 grant types enabled, and some
    clients have an ID and secret but are used to authenticate user logins!

    Put another way: having client credentials is *necessary but not sufficient*
    for this kind of usage.

.. toctree::
    :caption: Using Client Identities with the SDK
    :maxdepth: 1

    registering_a_client_identity
    using_client_app/index
