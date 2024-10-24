.. _timer_management_examples:

Timer Management
----------------

These examples demonstrate how to create, list, and delete timers with the SDK.

Create a timer
~~~~~~~~~~~~~~

This script creates a new timer, on source and destination collections provided
via the command-line. It syncs an input file or directory between the two.

The script assumes that the path being synced is the same on the source and
destination for simplicity.

.. note::
    This example does not handle ``data_access`` scope requirements.
    See the later example to handle this.

.. literalinclude:: create_timer.py
    :caption: ``create_timer.py`` [:download:`download <create_timer.py>`]
    :language: python

List timers
~~~~~~~~~~~

This script lists your current timers.

.. literalinclude:: list_timers.py
    :caption: ``list_timers.py`` [:download:`download <list_timers.py>`]
    :language: python

Delete a timer
~~~~~~~~~~~~~~

This script deletes a timer by ID.

.. literalinclude:: delete_timer.py
    :caption: ``delete_timer.py`` [:download:`download <delete_timer.py>`]
    :language: python

Create a timer with ``data_access``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script is similar to the ``create_timer.py`` example above. However, it
also handles ``data_access`` scope requirements for the source and destination
collections.

Discovering ``data_access`` requirements requires the use of a
``TransferClient`` to look up the collections.

As in the simpler example, this script creates a new timer, on source and
destination collections provided via the command-line. It syncs an input
file or directory between the two, and assumes that the path is the same on the
source and destination.

.. literalinclude:: create_timer_data_access.py
    :caption: ``create_timer_data_access.py`` [:download:`download <create_timer_data_access.py>`]
    :language: python
