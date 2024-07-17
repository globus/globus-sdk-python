
Initiating a Transfer
=====================

Moving data within the Globus Ecosystem can be performed by submitting a `Transfer Task`
to the Globus Transfer service.

The below example demonstrates how to submit that task using a ``TransferClient``.

.. note::
    The below example is for moving data between two publicly hosted "tutorial"
    collections.
    You should replace these collection ids and path values with your own collection
    ids and paths.

.. note::
    Some collections require you to attach a "data_access" scope to your transfer
    request. You should evaluate whether this is necessary for both your source and
    destination collections and omit the ``transfer_client.add_app_data_access_scope``
    calls as needed.

    A collection requires "data_access" if it is (1) a mapped collection and (2) is
    not high assurance.

    If you're still not able to determine, an alternative reactive script is included
    below.

.. literalinclude:: submit_transfer.py
    :caption: ``submit_transfer.py`` [:download:`download <submit_transfer.py>`]
    :language: python


Reactively solving ConsentRequired errors
------------------------------------------

Some collections require you to attach a "data_access" scope to your transfer
request.

This can be typically be done proactively: if you know which collections you or your
users will interacting with, you can evaluate whether they require this scope (they are
non-High Assurance mapped collections), and attach it through the client if so.

Sometimes however you do not know in advance the full range of collections that your
script will be interacting with. This script demonstrates how to reactively solve the
``ConsentRequired`` errors which are raised when a collection requires a "data_access"
scope but the client did not attach one.

.. note::
    Given that this script is reactive, it can involve two user login interactions
    where the above script only involves one.

.. literalinclude:: submit_transfer_reactive_consent_required.py
    :caption: ``submit_transfer_reactive_consent_required.py`` [:download:`download <submit_transfer_reactive_consent_required.py>`]
    :language: python
