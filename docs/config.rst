.. _config:

Globus SDK Configuration
========================

The behaviors of the SDK can be controlled either through environment variables,
or by passing parameters to clients and other objects.

.. note::

    SDK v1.x and v2.x supported the use of ``/etc/globus.cfg`` and
    ``~/.globus.cfg`` to set certain values. This feature was removed in v3.0 in
    favor of new environment variables for setting these values.

Environment Variables
---------------------

Each of these environment variables will be read automatically by the SDK.

Environment variables have lower precedence than explicit values set in
the interpreter. If ``GLOBUS_SDK_VERIFY_SSL="false"`` is set and a client is
created with ``verify_ssl=True``, the resulting client will have SSL
verification turned on.

``GLOBUS_SDK_VERIFY_SSL``
    Used to disable SSL verification, typically to handle SSL-intercepting
    firewalls. By default, all connections to servers are verified. Set
    ``GLOBUS_SDK_VERIFY_SSL="false"`` to disable verification.

``GLOBUS_SDK_HTTP_TIMEOUT``
    Adjust the timeout when HTTP requests are made. By default, requests have a
    60 second read timeout -- for slower responses, try setting
    ``GLOBUS_SDK_HTTP_TIMEOUT=120``

``GLOBUS_SDK_ENVIRONMENT``
    The name of the environment to use. Set ``GLOBUS_SDK_ENVIRONMENT="preview"``
    to use the Globus Preview environment.

``GLOBUS_SDK_SERVICE_URL_*``
    Override the URL used for a given service. The suffix of this environment variable
    must match the service name string used by the SDK in all caps (``SEARCH``,
    ``TRANSFER``, etc). For example, set
    ``GLOBUS_SDK_SERVICE_URL_TRANSFER="https://proxy-device.example.org/"`` to direct
    the SDK to use a custom URL when contacting the Globus Transfer service.

Config-Related Functions
------------------------

There are two functions available to translate the configuration described above into the URLs to use for accessing Globus services.

To return specifically the URL for the Globus Web App in a given environment:

.. autofunction:: globus_sdk.config.get_webapp_url

To return the URL for any other service in a given environment:

.. autofunction:: globus_sdk.config.get_service_url

Note that *no other imports* from ``globus_sdk.config`` are considered public.
