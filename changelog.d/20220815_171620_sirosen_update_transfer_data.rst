* Adjust behaviors of ``TransferData`` and ``TimerJob`` to make
  ``TimerJob.from_transfer_data`` work (:pr:`NUMBER`)
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
