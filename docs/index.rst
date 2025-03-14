Globus SDK for Python
=====================

.. module:: globus_sdk

This SDK provides a convenient Pythonic interface to
`Globus <https://www.globus.org>`_ web APIs,
including the Transfer API and the Globus Auth API. Documentation
for the APIs is available at https://docs.globus.org/api/.

Two interfaces are provided - a low level interface, supporting only
``GET``, ``PUT``, ``POST``, and ``DELETE`` operations, and a high level
interface providing helper methods for common API resources.

Additionally, some tools for interacting with local endpoint definitions are
provided.

Source code is available at https://github.com/globus/globus-sdk-python.

Table of Contents
-----------------

.. toctree::
    :caption: User Guide
    :maxdepth: 1

    user_guide/installation
    user_guide/getting_started/index

.. toctree::
    :caption: Full Reference
    :maxdepth: 2

    services/index
    local_endpoints
    Authorization <authorization/index>
    config
    core/index

.. toctree::
    :caption: Unstable
    :maxdepth: 1

    testing/index
    Experimental Components <experimental/index>
    experimental/examples/index

.. toctree::
    :caption: Examples
    :maxdepth: 1

    examples/index

.. toctree::
    :caption: Changes
    :maxdepth: 1

    versioning
    changelog
    upgrading

.. toctree::
    :caption: Additional Info
    :maxdepth: 1

    license
