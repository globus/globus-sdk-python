.. _globus_apps:

.. currentmodule:: globus_sdk

GlobusApps
==========

:class:`GlobusApp` is a high level construct designed to simplify the process of
of authenticating for Globus service clients.

A ``GlobusApp`` requires a programmatic Globus Auth entity called a "client" to be
supplied as the requester driving authentication flows. A client can be created and
managed as a part of a `Globus Project <https://app.globus.org/settings/developers>`_.
There are two types of GlobusApps; :class:`UserApp`, for contexts in which a client
should submit requests on behalf of a user, and :class:`ClientApp`, for contexts which
a client should submit requests on behalf of themselves.

The interfaces of these classes, defined below, intentionally include many
"sane defaults" (i.e., storing oauth2 access tokens in a json file). These defaults
may be overridden to customize the app's behavior. For more information on what
you can customize and how, see :ref:`globus_app_config`.

.. note::

    Currently ``GlobusApp`` only supports scripting-based use cases.

    Hosted applications (i.e. web servers) should see :ref:`globus_authorizers` instead.


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
