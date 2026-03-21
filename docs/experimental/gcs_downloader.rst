.. _gcs_downloader:

.. currentmodule:: globus_sdk.experimental.gcs_downloader

GCS Downloader
==============

A :class:`GCSDownloader` is an object which handles connections to an
HTTPS-enabled collection and single file downloads over HTTPS.

It primarily features two APIs:

1. Initialization and use as a context manager
2. :meth:`GCSDownloader.read_file` to get a single file by URL

.. autoclass:: GCSDownloader
    :members:
    :member-order: bysource

Example Usage
-------------

In this example, a ``GCSDownloader`` with a ``GlobusApp`` completely handles
the authentication process for an HTTPS file download, which is then printed
to stdout.

.. code-block:: python

    import globus_sdk
    from globus_sdk.experimental.gcs_downloader import GCSDownloader

    # SDK Tutorial Client ID - <replace this with your own client>
    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

    # this example is a path on the Globus Tutorial Collections
    FILE_URL = (
        "https://m-d3a2c3.collection1.tutorials.globus.org/home/share/godata/file2.txt"
    )

    with globus_sdk.UserApp("gcs-downloader-demo", client_id=CLIENT_ID) as app:
        with GCSDownloader(app) as downloader:
            print(downloader.read_file(FILE_URL))

.. note::

    This example will require you to log in twice the first time you run it.
    This is normal behavior and is a consequence of needing to be logged in to
    discover authentication requirements.
