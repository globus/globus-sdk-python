.. image:: https://github.com/globus/globus-sdk-python/workflows/build/badge.svg?event=push
    :alt: build status
    :target: https://github.com/globus/globus-sdk-python/actions?query=workflow%3Abuild

.. image:: https://img.shields.io/pypi/v/globus-sdk.svg
    :alt: Latest Released Version
    :target: https://pypi.org/project/globus-sdk/

.. image:: https://img.shields.io/pypi/pyversions/globus-sdk.svg
    :alt: Supported Python Versions
    :target: https://pypi.org/project/globus-sdk/

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :alt: License
    :target: https://opensource.org/licenses/Apache-2.0

.. image:: https://results.pre-commit.ci/badge/github/globus/globus-sdk-python/main.svg
   :target: https://results.pre-commit.ci/latest/github/globus/globus-sdk-python/main
   :alt: pre-commit.ci status

..
    This is the badge style used by the isort repo itself, so we'll use their
    preferred colors

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :alt: Import Style
    :target: https://pycqa.github.io/isort/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style
    :target: https://github.com/psf/black


Globus SDK for Python
=====================

This SDK provides a convenient Pythonic interface to
`Globus <https://www.globus.org>`_ APIs.

Basic Usage
-----------

Install with ``pip install globus-sdk``

You can then import Globus client classes and other helpers from
``globus_sdk``. For example:

.. code-block:: python

    from globus_sdk import LocalGlobusConnectPersonal

    # None if Globus Connect Personal is not installed
    endpoint_id = LocalGlobusConnectPersonal().endpoint_id


Testing, Development, and Contributing
--------------------------------------

Go to the
`CONTRIBUTING <https://github.com/globus/globus-sdk-python/blob/main/CONTRIBUTING.adoc>`_
guide for detail.

Links
-----
| Full Documentation: http://globus-sdk-python.readthedocs.io/
| Source Code: https://github.com/globus/globus-sdk-python
| API Documentation: https://docs.globus.org/api/
| Release History + Changelog: https://github.com/globus/globus-sdk-python/releases
