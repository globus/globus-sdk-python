.. _globus_apps:

.. currentmodule:: globus_sdk

GlobusApps
==========


.. warning::

    Currently ``GlobusApp`` only supports scripting-based use cases.

    Hosted applications (i.e. web servers) should see :ref:`globus_authorizers` instead.


:class:`GlobusApp` is a high level construct designed to simplify the process of
of authenticating for Globus service clients.

A ``GlobusApp`` always requires that a programmatic entity called a "client" be supplied
as the requester driving authentication flows. Depending on the type of ``GlobusApp``
being used, the client will either facilitate service interactions for a human
or interact with services as a distinct entity itself.

*   A :class:`UserApp` drives interaction starting with a browser based login
    flow. With this type of ``GlobusApp``, newly created resources (collections,
    flows, etc.) are owned by the human user who completed the login flow.
    Similarly resource access is evaluated based on that user's permissions.

    A :class:`UserApp` should be used in cases where a script simplifies a process
    for a user, but the user is ultimately responsible for the actions taken by the
    script. This type of ``GlobusApp`` typically should use a "native"-type client.
    "Confidential"-type clients are allowed, but prove more difficult to configure.

*   A :class:`ClientApp` by contrast does not require any manual login flow. Instead
    newly created resources (collections, flows, etc.) are owned by the client
    itself, not a human. Similarly, resource access will be evaluated based on the
    client's permissions.

    A :class:`ClientApp` should be used in automation cases in which a service account,
    potentially managed by multiple humans, is responsible for the actions taken by
    the script or process. This type of ``GlobusApp`` **must use a "confidential"-type
    client**. "Native"-type clients don't have the necessary security properties (a
    client secret) to own their own resources (and thus will be rejected).

    .. note::

        Not all Globus services support ``ClientApp``-based interactions.

        Certain GCS collections, for instance, require that a human user has
        authenticated with their university email recently before allowing data
        movement. In these cases, a ``UserApp`` must be used instead.


Both "native" and "confidential" type clients, may be created and managed as a part
of a `Globus Project <https://app.globus.org/settings/developers>`_.

The interfaces of these classes, defined below, intentionally include many
"sane defaults" (i.e., storing oauth2 access tokens in a json file). These defaults
may be overridden to customize the app's behavior. For more information on what
you can customize and how, see :ref:`globus_app_config`.


Reference
---------

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
