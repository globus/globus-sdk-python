
Initiating a Transfer
=====================

Moving data within the Globus Ecosystem is performed by submitting a ``Transfer Task``
against the Globus Transfer service.

The below examples demonstrate how to do that using a globus sdk ``TransferClient``.
They are split into two categories:

#. :ref:`transferring-between-known-collections` - both source and destination
   collections are known in advance and are likely be hardcoded into your script.

#. :ref:`transferring-between-unknown-collections` - either the source or
   destination collection will be determined at runtime (e.g. by script argument).

The examples are differentiated because certain collections require a special scope
("data_access") to be attached to the transfer request. If both collections are known
this can be done proactively after determining whether the collections will require it.
If, however, one or more collections are unknown


.. _transferring-between-known-collections:

Transferring data between two known collections
-----------------------------------------------

.. note::
    The script references two globus hosted "tutorial" collections. Replace these ids &
    paths with your own collection ids and paths to move your own data.

.. note::
    Some collections require you to attach a "data_access" scope to your transfer
    request. You should evaluate whether this is necessary for both your source and
    destination collections and omit the ``transfer_client.add_app_data_access_scope``
    calls as needed.

    A collection requires "data_access" if it is (1) a mapped collection and (2) is
    not high assurance.

.. literalinclude:: submit_transfer_collections_known.py
    :caption: ``submit_transfer_collections_known.py`` [:download:`download <submit_transfer_collections_known.py>`]
    :language: python


.. _transferring-between-unknown-collections:

Transferring data where at least one collection is unknown
----------------------------------------------------------

In the case where your script does not know the full set of collections that it will
be interacting with, you may need to reactively solve the ``ConsentRequired`` errors
instead of proactively attaching the "data_access" scope.

This script demonstrates how to do that by:

#. Attempting to submit the transfer without any "data_access" scopes.
#. Intercepting any raised ``ConsentRequired`` errors if the request fails.
#. Attaching any scope requirements detailed in the error.
#. Retrying the transfer which implicitly puts your user through a consent flow to
   resolve their auth state.

.. note::
    The script references two globus hosted "tutorial" collections. Replace these ids &
    paths with your own collection ids and paths to move your own data.

.. note::
    Given that this script reactively fixes auth states, it can involve two user login
    interactions instead of the one required by the above proactive approach.

.. literalinclude:: submit_transfer_collections_unknown.py
    :caption: ``submit_transfer_collections_unknown.py`` [:download:`download <submit_transfer_collections_unknown.py>`]
    :language: python
