Breaking Changes
----------------

- The ``TimerJob.from_transfer_data`` classmethod, which was deprecated in
  globus-sdk version 3, has been removed. Users should use the ``TransferTimer``
  class to construct timers which submit transfer tasks. (:pr:`NUMBER`)
