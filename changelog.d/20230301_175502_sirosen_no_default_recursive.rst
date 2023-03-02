* ``TransferData.add_item`` now defaults to omitting ``recursive`` rather than
  setting its value to ``False``. This change better matches new Transfer API
  behaviors which treat the absence of the ``recursive`` flag as meaning
  autodetect, rather than the previous default of ``False``. Setting the
  recursive flag can still have beneficial behaviors, but should not be
  necessary for many use-cases (:pr:`NUMBER`)
