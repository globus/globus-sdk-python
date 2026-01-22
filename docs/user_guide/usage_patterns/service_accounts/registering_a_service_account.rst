.. _userguide_register_service_account:

Registering a Service Account
=============================

In order to be used as a Service Account or "Client Identity", a client must
be registered in Globus Auth under the correct type.

This is similar to the
:ref:`getting started documentation on registering an app <tutorial_register_app>`,
but using some different settings.

Creating the Client
-------------------

The following steps will walk you through how to register a client for use as a
service account.
One topic not covered here is how to securely store and manage your secrets --
the guidance below will simply say "save", and it is the user's responsibility
to decide how to save and secure these credentials.

1.  Navigate to the `Developer Site <https://app.globus.org/settings/developers>`_

2.  Select "Register a service account or application credential for automation"

3.  Create or Select a Project

    * A project is a collection of apps with a shared list of administrators.
    * If you don't own any projects, you will automatically be prompted to create one.
    * If you do, you will be prompted to either select an existing or create a new one.

4.  Creating or selecting a project will prompt you for another login, sign in with an
    account that administers your project.

5.  Give your App a name. This will appear as the identity's "name" where a
    user's full name might appear.

6.  Click "Register App". This will create your app and take you to a page
    describing it.

7.  Copy the "Client UUID" and save it -- this is your ``client_id`` in the
    Python SDK's terms.

8.  Click "Add Client Secret", fill in the label, and save the secret -- this is
    your ``client_secret`` in the Python SDK's terms.


Saving and Retrieving Client IDs and Secrets
--------------------------------------------

The Globus SDK does not offer special capabilities for storage and retrieval of
client IDs and client secrets.

In examples in SDK documentation, you will see the client ID and secret written
as hardcoded constants, e.g.

.. code-block:: python

    import globus_sdk

    CLIENT_ID = "YOUR ID HERE"
    CLIENT_SECRET = "YOUR SECRET HERE"

    client = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)

You can replace those variables with sources of your choice.
For example, you could make them environment variables:

.. code-block:: python

    import os

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    if not (CLIENT_ID and CLIENT_SECRET):
        raise RuntimeError("CLIENT_ID and CLIENT_SECRET must both be set.")

Selecting an appropriate storage and retrieval mechanism for client credentials
is considered a user responsibility by the SDK.
