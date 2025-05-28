Scopes and Consents
===================

Globus uses OAuth2 scopes to control access to different APIs and allow
applications provide a least-privilege security guarantee to their users.

Overview
--------

A "Consent" is a record, in Globus Auth, that an application is allowed to take
some action on behalf of a user. A "Scope" is the name of some action or set of
actions.

For example, ``urn:globus:auth:scope:groups.api.globus.org:all`` is a scope
which gives full access to Globus Groups. Users _consent_ to allow applications,
like the Globus CLI, to get credentials which are "valid for this scope", and
thereby to view and manipulate their group memberships.

For more information, see
`this docs.globus.org explanation of scopes and consents
<https://docs.globus.org/guides/overviews/clients-scopes-and-consents/>`_.

Reference
---------

Within the Globus SDK, Scopes and Consents are modeled using several objects
which make learning about and manipulating these data easier.

.. toctree::
    :maxdepth: 1

    scopes
    consents
