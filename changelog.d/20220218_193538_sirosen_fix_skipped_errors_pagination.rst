* Fix the pagination behavior for ``TransferClient`` on ``task_skipped_errors`` and
  ``task_successful_transfers``, and apply the same fix to the endpoint manager
  variants of these methods. Prior to the fix, paginated calls would return a
  single page of results and then stop (:pr:`NUMBER`)
