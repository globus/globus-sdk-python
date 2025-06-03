Globus Timers
=============

.. currentmodule:: globus_sdk

.. autoclass:: TimersClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

A helper is provided for constructing Transfer Timers:

.. autoclass:: TransferTimer
   :members:
   :show-inheritance:

In order to schedule a timer, pass a ``schedule`` with relevant parameters.
This can be done using the two schedule helper classes

.. autoclass:: OnceTimerSchedule
   :members:
   :show-inheritance:

.. autoclass:: RecurringTimerSchedule
   :members:
   :show-inheritance:

TimerJob (legacy)
~~~~~~~~~~~~~~~~~

The ``TimerJob`` class is still supported for creating timers, but it is
not recommended.
New users should prefer the ``TransferTimer`` class.

.. autoclass:: TimerJob
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs on calls to the Timers service, a :class:`TimersClient`
will raise a ``TimersAPIError``.

.. autoclass:: TimersAPIError
   :members:
   :show-inheritance:
