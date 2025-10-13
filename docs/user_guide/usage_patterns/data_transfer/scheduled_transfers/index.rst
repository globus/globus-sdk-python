.. currentmodule:: globus_sdk

.. _userguide_scheduled_transfers:

Scheduling a Repeating Transfer
===============================

The Globus Timers service allows users to schedule tasks to run at a future
date or on a recurring schedule.
In particular, Timers allows scheduled ``Transfer Tasks``, which can be
submitted very similarly to submissions to the Globus Transfer service.

Creating a Transfer Timer
-------------------------

To setup recurring transfers, you will need to create a timer.
The timer *contains* a Transfer Task submission.
It will submit that Transfer Task each time it runs.

.. literalinclude:: create_timer.py
    :caption: ``create_timer.py`` [:download:`download <create_timer.py>`]
    :language: python


Discover Data Access Scopes and Create a Timer
----------------------------------------------

Unlike direct ``Transfer Task`` submission, creating a Timer with unknown inputs
won't give you an error immediately if you need ``data_access`` scopes because
that information isn't available until the Timer runs.

Therefore, if the input collections are variable, we need to enhance the previous
example to automatically determine whether or not the ``data_access`` scope is
needed.
We'll do this with a new ``uses_data_access`` helper and a :class:`TransferClient`:

.. code-block:: python

    with globus_sdk.TransferClient(app=app) as transfer_client:
        ...  # a code block which can use the helper


    def uses_data_access(client: globus_sdk.TransferClient, collection_id: str) -> bool:
        """
        Lookup the given collection ID.
        Having looked up the record, return `True` if it uses a `data_access` scope
        and `False` otherwise.
        """
        doc = client.get_endpoint(collection_id)
        if doc["entity_type"] != "GCSv5_mapped_collection":
            return False
        if doc["high_assurance"]:
            return False
        return True

This will allow us to guard our use of the ``data_access`` scope thusly:

.. code-block:: python

    if uses_data_access(transfer_client, SRC_COLLECTION):
        timers_client.add_app_transfer_data_access_scope(SRC_COLLECTION)
    if uses_data_access(transfer_client, DST_COLLECTION):
        timers_client.add_app_transfer_data_access_scope(DST_COLLECTION)

.. note::

    Because the ``data_access`` requirement can't be detected until after you have
    logged in to the app, it is possible for this to result in a "double login"
    scenario. First, you login providing consent for Timers and Transfer, but
    then a ``data_access`` scope is found to be needed. You then have to login
    again to satisfy that requirement.

    The ``UserApp`` will track the addition until you use ``app.logout``,
    however, so this only happens the first time the script runs.

With these modifications in place, the resulting script looks like so:

.. literalinclude:: create_timer_detect_data_access.py
    :caption: ``create_timer_detect_data_access.py`` [:download:`download <create_timer_detect_data_access.py>`]
    :language: python
