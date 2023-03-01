* ``TransferData.add_item`` now defaults to omitting ``recursive`` rather than
  setting its value to ``False``. This change better matches new Transfer API
  behaviors which treat the absence of the ``recursive`` flag as meaning
  autodetect, rather than the previous default of ``False``. Users are
  recommended to avoid explicitly setting the value unless they would like
  to avoid using the autodetection logic (:pr:`NUMBER`)
