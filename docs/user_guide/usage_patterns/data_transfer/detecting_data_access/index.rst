.. currentmodule:: globus_sdk

.. _userguide_detecting_data_access:

Detecting data_access
=====================

Globus Collections come in several varieties, but only some of them have a
``data_access`` scope.

``data_access`` scopes control application access to collections, allowing
users to revoke access for an application independent from other application
permissions.
Revoking consent stops data transfers and other operations.

Because only some collection types have ``data_access`` scopes, application
authors interacting with these collections may need to detect the type of
collection and determine whether or not the scope will be needed.

For readers who prefer to start with complete working examples, jump ahead to the
:ref:`example script <userguide_detecting_data_access_example>`.

Accessing Collections in Globus Transfer
----------------------------------------

The Globus Transfer service acts as a central registration hub for collections.
Therefore, in order to get information about an unknown collection, we will
need a :class:`TransferClient` with credentials.

The following snippet creates a client and uses it to fetch a collection from
the service:

.. code-block:: python

    import globus_sdk

    # Tutorial Client ID - <replace this with your own client>
    NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

    # Globus Tutorial Collection 1
    # https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
    # replace with your own COLLECTION_ID
    COLLECTION_ID = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"


    with globus_sdk.UserApp(
        "detect-data-access-example", client_id=NATIVE_CLIENT_ID
    ) as app:
        transfer_client = globus_sdk.TransferClient(app=app)
        collection_doc = transfer_client.get_endpoint(COLLECTION_ID)

.. note::

    Careful readers may note that we use the :meth:`TransferClient.get_endpoint`
    method to lookup a collection.

    The Transfer service contains both Endpoints and Collections,
    and both document types are available from the Get Endpoint API.


Reading Collection Type
-----------------------

There are two attributes we need from the collection document to determine
whether or not a ``data_access`` scope is used.

First, whether or not the collection is a GCSv5 Mapped Collection:

.. code-block:: python

    entity_type = collection_doc["entity_type"]
    is_v5_mapped_collection = entity_type == "GCSv5_mapped_collection"

Second, whether or not the collection is a High Assurance Collection:

.. code-block:: python

    is_high_assurance = collection_doc["high_assurance"]

Once we have this information, we can deduce whether or not ``data_access`` is
needed with the following boolean assignment:

.. code-block:: python

    collection_uses_data_access = is_v5_mapped_collection and not is_high_assurance

Converting Logic to a Helper Function
-------------------------------------

In order to make the logic above reusable, we need to rephrase.
One of the simpler approaches is to define a helper function which accepts the
:class:`TransferClient` and collection ID as inputs.

Here's a definition of such a helper which is broadly applicable:

.. code-block:: python

    def uses_data_access(
        transfer_client: globus_sdk.TransferClient, collection_id: str
    ) -> bool:
        """
        Use the provided `transfer_client` to lookup a collection by ID.

        Return `True` if the collection uses a `data_access` scope
        and `False` otherwise.
        """
        doc = transfer_client.get_endpoint(collection_id)
        if doc["entity_type"] != "GCSv5_mapped_collection":
            return False
        if doc["high_assurance"]:
            return False
        return True

Guarding ``data_access`` Scope Handling
---------------------------------------

Now that we have a reusable helper for determining whether or not collections
use a ``data_access`` scope, it's possible to use this to drive logic for scope
manipulations.

For example, we can choose to add ``data_access`` requirements to a
:class:`GlobusApp` like so:

.. code-block:: python

    # Globus Tutorial Collection 1 & 2
    # https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
    # https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
    # replace with your desired collections
    SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
    DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"

    if uses_data_access(transfer_client, SRC_COLLECTION):
        transfer_client.add_app_data_access_scope(SRC_COLLECTION)
    if uses_data_access(transfer_client, DST_COLLECTION):
        transfer_client.add_app_data_access_scope(DST_COLLECTION)

.. _userguide_detecting_data_access_example:

Summary: Complete Example
-------------------------

With these modifications in place, we can compile the above tooling into a
complete script.

*This example is complete. It should run without errors "as is".*

.. literalinclude:: submit_transfer_detect_data_access.py
    :caption: ``submit_transfer_detect_data_access.py`` [:download:`download <submit_transfer_detect_data_access.py>`]
    :language: python

.. note::

    Because the ``data_access`` requirement can't be detected until after you have
    logged in to the app, it is possible for this to result in a "double login"
    scenario.
    First, you login providing consent for Transfer, but then a ``data_access``
    scope is found to be needed.
    You then have to login again to satisfy that requirement.
