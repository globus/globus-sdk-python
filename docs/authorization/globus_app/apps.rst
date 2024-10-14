.. _globus_apps:

.. currentmodule:: globus_sdk

GlobusApps
==========


.. note::

    Currently ``GlobusApp`` can only be used in scripts (e.g., notebooks or automation)
    and applications directly responsible for a user's login flow.

    Web services and other hosted applications operating as an OAuth2 resource server
    should see :ref:`globus_authorizers` instead.


:class:`GlobusApp` is a high level construct designed to simplify authentication for
interactions with :ref:`globus-sdk services <services>`.

A ``GlobusApp`` uses an OAuth2 client to obtain and manage OAuth2 tokens required for
API interactions. OAuth2 clients must be created external to the SDK by registering an
application at the
`Globus Developer's Console <https://app.globus.org/settings/developers>`_.

The following section provides a comparison of the specific types of ``GlobusApps``
to aid in selecting the proper one for your use case.

Types of GlobusApps
-------------------

There are two flavors of ``GlobusApp`` available in the SDK:

*   :class:`UserApp`, for interactions in which an end user communicates with Globus
    services and
*   :class:`ClientApp`, for interactions in which an OAuth2 client, operating as a
    "service account", communicates with Globus services.

The following table provides a comparison of these two options:


.. list-table::
    :widths: 50 50
    :header-rows: 1

    *   - **UserApp**
        - **ClientApp**

    *   - Appropriate for performing actions as a specific end user (e.g., the
          `Globus CLI <https://docs.globus.org/cli/>`_)
        - Appropriate for automating actions as a service account

    *   - Created resources (e.g., collections or flows) by default are owned by an end
          user
        - Created resources (e.g., collections or flows) by default are owned by the
          OAuth2 client

    *   - Existing resource access is evaluated based on an end user's permissions
        - Existing resource access is evaluated based on the OAuth2 client's permissions

    *   - OAuth2 tokens are obtained by putting an end user through a login flow
          (this occurs in a web browser)
        - OAuth2 tokens are obtained by programmatically exchanging an OAuth2 client's
          secret

    *   - Should typically use a "native" OAuth2 client (`Register a thick client
          <https://app.globus.org/settings/developers/registration/public_installed_client>`_)

          May use a "confidential" OAuth2 client (`Register a portal or science gateway
          <https://app.globus.org/settings/developers/registration/confidential_client>`_)
        - Must use a "confidential" OAuth2 client

          (`Register a service account
          <https://app.globus.org/settings/developers/registration/client_identity>`_)


.. note::

    Not all Globus operations support both app types.

    Particularly when dealing with sensitive data, services may enforce that a
    a user be the primary data access actor. In these cases, a ``ClientApp``
    will be rejected and a ``UserApp`` must be used instead.

Reference
---------

The interfaces of these classes, defined below, intentionally include many
"sane defaults" (i.e., storing oauth2 access tokens in a json file). These defaults
may be overridden to customize the app's behavior. For more information on what
you can customize and how, see :ref:`globus_app_config`.

..  autoclass:: GlobusApp()
    :members:
    :exclude-members: scope_requirements
    :member-order: bysource

..
    In the above class, "scope_requirements" is excluded because it's an `@property`.
    Sphinx wants to document it as a method but that's not how it's invoked. Instead
    documentation is included in the class docstring as an `ivar`.

Implementations
^^^^^^^^^^^^^^^

..  autoclass:: UserApp
    :members:

..  autoclass:: ClientApp
    :members:
