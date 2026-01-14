.. _userguide_using_client_app:

Using a ClientApp with a Service Account
========================================

Once you have a client ID and secret from an app registration for a service
account, the SDK has a few tools which can use those credentials to acquire
tokens, to talk to various Globus Services.

The easiest tool for this job is a ``ClientApp``, a flavor of ``GlobusApp``
designed to work with service accounts.

Instantiating a ClientApp
-------------------------

Constructing an app takes three required parameters,

- a human readable name to identify your app in HTTP requests and token caching (e.g., "My Cool Weathervane").
   - this does not need match the name you supplied during client registration.
- the client ID
- the client secret

as in:

.. code-block:: python

    import globus_sdk

    CLIENT_ID = "YOUR ID HERE"
    CLIENT_SECRET = "YOUR SECRET HERE"

    app = globus_sdk.ClientApp(
        "sample-app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

Using the App with a Globus Service
-----------------------------------

The resulting app can then be passed to any SDK client class to create an API
client object which uses the app for authentication requirements.
For example, to use the ``app`` object to run an ``ls`` on one of the tutorial
collections:

.. code-block:: python

    TUTORIAL_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"

    with globus_sdk.TransferClient(app=app) as tc:
        tc.add_app_data_access_scope(TUTORIAL_COLLECTION)
        ls_result = tc.operation_ls(TUTORIAL_COLLECTION, path="/home/share/godata")

.. note::

    Unfortunately, there are two different meanings of the word "client" in use
    in this example!

    A ``TransferClient`` is a "client" in the sense that it is a local object
    which provides access to the Globus Transfer Service.
    The ``CLIENT_ID``, ``CLIENT_SECRET``, and ``ClientApp`` are all using the
    word "client" in reference to the OAuth2 standard's definition of a "client"
    as a registered app, a different meaning for the same word.

Using Memory Storage
--------------------

Unlike user logins, client credentials can't be "logged out" vs "logged in" --
unless they are deleted via the Globus Auth service, they are always active.

As a result, unlike applications which provide user logins, ``ClientApp``\s will
very often prefer to store any tokens they are using in memory. The tokens will
be cached and reused over the lifetime of the process, but never persisted to
disk.

To configure an app in this way, simply add a ``config`` to the app
initialization to select the ``"memory"`` storage type:

.. code-block:: python

    app = globus_sdk.ClientApp(
        "sample-app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        config=globus_sdk.GlobusAppConfig(token_storage="memory"),
    )

Complete Example
----------------

In addition to leveraging all of the elements described above, this example enhances the code sample to
use the ``ClientApp``'s context manager interface to close token storage.
We also add a loop of ``print()`` usages on the ``ls`` result to show some output:

.. literalinclude:: client_app_ls.py
    :caption: ``client_app_ls.py`` [:download:`download <client_app_ls.py>`]
    :language: python
