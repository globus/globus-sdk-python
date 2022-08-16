* Adjust behaviors of ``TransferData`` and ``TimerJob`` to make
  ``TimerJob.from_transfer_data`` work and to defer requesting the
  ``submission_id`` until the task submission call (:pr:`NUMBER`)
** ``TransferData`` avoids passing ``null`` for several values when they are
   omitted, ranging from optional parameters to ``add_item`` to
   ``skip_activation_check``
** ``TransferData`` and ``DeleteData`` now support usage in which the
    ``transfer_client`` parameters is ``None``. In these cases, if
    ``submission_id`` is omitted, it will be omitted from the document,
    allowing the creation of a partial task submsision document with no
    ``submission_id``
** ``TimerJob.from_transfer_data`` will now raise a ``ValueError`` if the input
   document contains ``submission_id`` or ``skip_activation_check``
** ``TransferClient.submit_transfer`` and ``TransferClient.submit_delete`` now
   check to see if the data being sent contains a ``submission_id``. If it does
   not, ``get_submission_id`` is called automatically and set as the
   ``submission_id`` on the payload. The new ``submission_id`` is set on the
   object passed to these methods, meaning that these methods are now
   side-effecting.

The newly recommended usage for ``TransferData`` and ``DeleteData`` is to pass
the endpoints as named parameters:

.. code-block:: python

    # -- for TransferData --
    # old usage
    transfer_client = TransferClient()
    transfer_data = TransferData(transfer_client, ep1, ep2)
    # new (recommended) usage
    transfer_data = TransferData(source_endpoint=ep1, destination_endpoint=ep2)

    # -- for DeleteData --
    # old usage
    transfer_client = TransferClient()
    delete_data = TransferData(transfer_client, ep)
    # new (recommended) usage
    delete_data = DeleteData(endpoint=ep)
