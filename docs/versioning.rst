.. _versioning:

Versioning Policy
=================

The Globus SDK follows `Semantic Versioning <https://semver.org/>`_.

That means that we use version numbers of the form **MAJOR.MINOR.PATCH**.

When the SDK needs to make incompatible API changes, the **MAJOR** version
number will be incremented. **MINOR** and **PATCH** version increments indicate
new features or bugfixes.

Public Interfaces
-----------------

Features documented here are public and all other components of the SDK should
be considered private. Undocumented components may be subject to backwards
incompatible changes without increments to the **MAJOR** version.

Recommended Pinning
-------------------

We recommend that users of the SDK pin only to the major version which they
require. e.g. specify ``globus-sdk>=3.7,<4.0`` in your package requirements.

Upgrade Caveat
--------------

It is always possible for new features or bugfixes to cause issues.

If you are installing the SDK into mission-critical production systems, we
strongly encourage you to establish a method of pinning the exact version used
and testing upgrades.

Deprecation Warnings
--------------------

``globus-sdk`` will emit deprecation warnings for features which are removed in
the next release. The Python interpreter applies a filter by default which
ignores all deprecation warnings.

Users are can enable deprecation warnings by normal Python mechanisms. e.g. By
applying a filter:

.. code-block:: python

    import warnings

    warnings.simplefilter("default")  # this enables DeprecationWarnings
