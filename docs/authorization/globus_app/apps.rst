.. _globus_apps:

.. currentmodule:: globus_sdk

GlobusApps
==========


.. warning::

    Currently ``GlobusApp`` only supports scripting-based use cases.

    Hosted applications (i.e. web servers) should see :ref:`globus_authorizers` instead.


:class:`GlobusApp` is a high level construct designed to simplify the process of
of authenticating for Globus service clients.

A ``GlobusApp`` will always require a programmatic entity called a "client". Depending
on the type of ``GlobusApp`` in use, the client will play different roles in the
request flow.

*   A :class:`UserApp` drives interaction starting with a browser based login
    flow. With this type of ``GlobusApp``, newly created resources (collections,
    flows, etc.) are owned by the human user who has logged in (and thus granted the
    app authorization tokens). Similarly resource access is evaluated based on that
    user's permissions.

    A :class:`UserApp` should be used in cases where a script simplifies a process
    for a user, but the user is ultimately responsible for the actions taken by the
    script. The `Globus CLI <https://docs.globus.org/cli/>`_ is a good example of
    one such use case.

    A :class:`UserApp` **should use a "native"-type client**. "Confidential"-type
    clients are allowed, but prove more difficult to configure.

*   A :class:`ClientApp` by contrast does not require any manual login flow. Instead
    newly created resources (collections, flows, etc.) are owned by the client
    itself, not a human. Similarly, resource access will be evaluated based on the
    client's permissions.

    A :class:`ClientApp` should be used in cases where a service account, potentially
    managed by multiple humans, is responsible for the actions taken by the script or
    process. These cases mostly involve some kind of automation, i.e., frequent data
    movement or flow invocation.

    A :class:`ClientApp` **must use a "confidential"-type client**. "Native"-type
    clients don't have the necessary security properties (a client secret) to own their
    own resources and will be rejected.

    .. note::

        Not all Globus services or contexts support ``ClientApp``-based interactions.

        GCS collections with sensitive data, for instance, may require that a human user
        has authenticated with their university email recently before allowing data
        interaction. In these cases, a ``UserApp`` must be used instead.


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
