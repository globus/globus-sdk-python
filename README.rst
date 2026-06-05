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
`CONTRIBUTING <https://github.com/globus/globus-sdk-python/blob/main/CONTRIBUTING.rst>`_
guide for detail.

Links
-----
| Full Documentation: https://globus-sdk-python.readthedocs.io/
| Source Code: https://github.com/globus/globus-sdk-python
| API Documentation: https://docs.globus.org/api/
| Release History + Changelog: https://github.com/globus/globus-sdk-python/releases
