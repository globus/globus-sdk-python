.. _example_minimal_transfer:

File Transfer Scripts
=====================

Minimal File Transfer Script
----------------------------

The following is an extremely minimal script to demonstrate a file transfer
using the :class:`TransferClient <globus_sdk.TransferClient>`.

It uses the tutorial client ID from the :ref:`tutorials <tutorials>`.
For simplicity, the script will prompt for login on each use.

.. note::
    You will need to replace the values for ``source_collection_id`` and
    ``dest_collection_id`` with UUIDs of collections that you have access to.

.. literalinclude:: transfer_minimal.py
    :caption: ``transfer_minimal.py`` [:download:`download <transfer_minimal.py>`]
    :language: python


Minimal File Transfer Script Handling ConsentRequired
-----------------------------------------------------

The above example works with certain endpoint types, but will fail if either
the source or destination endpoint requires a ``data_access`` scope. This
requirement will cause the Transfer submission to fail with a
``ConsentRequired`` error.

The example below catches the ``ConsentRequired`` error and retries the
submission after a second login.

This kind of "reactive" handling of ``ConsentRequired`` is the simplest
strategy to design and implement.

We'll also enhance the example to take endpoint IDs from the command line.

.. literalinclude:: transfer_consent_required_reactive.py
    :caption: ``transfer_consent_required_reactive.py`` [:download:`download <transfer_consent_required_reactive.py>`]
    :language: python


Best-Effort Proactive Handling of ConsentRequired
-------------------------------------------------

The above example works in most cases, and especially when there is a low cost
to failing and retrying an activity.

However, in some cases, responding to ``ConsentRequired`` errors when the task
is submitted is not acceptable. For example, for scripts used in batch job
systems, the user cannot respond to the error until the job is already
executing. The user would rather handle such issues when submitting their job.

``ConsentRequired`` errors in this case can be avoided on a best-effort basis.
Note, however, that the process for consenting ahead of time is more error
prone and complex.

The example below enhances the previous reactive error handling to try an
``ls`` operation before starting to build the task data. If the ``ls`` fails
with ``ConsentRequired``, the user can be put through the relevant login flow.
And if not, we can relatively safely assume that any errors are not relevant.

.. literalinclude:: transfer_consent_required_proactive.py
    :caption: ``transfer_consent_required_proactive.py`` [:download:`download <transfer_consent_required_proactive.py>`]
    :language: python
