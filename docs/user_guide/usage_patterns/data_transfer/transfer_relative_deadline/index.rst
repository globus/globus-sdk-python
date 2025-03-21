.. currentmodule:: globus_sdk

.. _userguide_transfer_relative_deadline:

Setting a Relative Deadline for a Transfer
==========================================

When transferring or deleting data via Globus Transfer, users are able to set a
``deadline`` for their tasks.
This allows you to declare a time by which the task must be completed -- if the
deadline is reached and the task is still in progress, it will be cancelled.

The ``deadline`` field in a Transfer task takes a date and time in ISO 8601
format. Because of the use of a standard format, it is easy to use the Python
``datetime`` module to compute a relative deadline at some point in the future.
You can use this to easily submit tasks with deadlines limited to the next minute,
hour, or day.
You can use this, for example, to enforce that a Transfer Task which takes too
long results in errors (even if it is making slow progress).

For readers who prefer to start with complete working examples, jump ahead to the
:ref:`example script <userguide_transfer_relative_deadline_example>`.

Computing and Formatting a Deadline
-----------------------------------

We need to compute a relative deadline -- some point into the future -- and
format it as a string.
We'll express that idea in a function which takes a :class:`datetime.timedelta`
as an ``offset``, an amount of time into the future.
This gives us a generic phrasing of getting a future date:

.. code-block:: python

    import datetime


    def make_relative_deadline(offset: datetime.timedelta) -> str:
        now = datetime.datetime.now(tz=datetime.UTC)
        deadline = now + offset
        return deadline.isoformat()

We can then see that this works by testing it out:

.. code-block:: pycon

    >>> make_relative_deadline(datetime.timedelta(minutes=10))
    '2003-09-21T18:58:09.279314+00:00'

Creating a Task with the Deadline
---------------------------------

``deadline`` is an initialization parameter to :class:`TransferData` and
:class:`DeleteData`.
Along with all of our other parameters to create the Transfer Task, here's
a sample task document with a deadline set for "an hour from now":

.. code-block:: python

    # Globus Tutorial Collection 1
    # https://app.globus.org/file-manager/collections/6c54cade-bde5-45c1-bdea-f4bd71dba2cc
    SRC_COLLECTION = "6c54cade-bde5-45c1-bdea-f4bd71dba2cc"
    SRC_PATH = "/share/godata/file1.txt"

    # Globus Tutorial Collection 2
    # https://app.globus.org/file-manager/collections/31ce9ba0-176d-45a5-add3-f37d233ba47d
    DST_COLLECTION = "31ce9ba0-176d-45a5-add3-f37d233ba47d"
    DST_PATH = "/~/example-transfer-script-destination.txt"

    # create a Transfer Task request document, including a relative deadline
    transfer_request = globus_sdk.TransferData(
        source_endpoint=SRC_COLLECTION,
        destination_endpoint=DST_COLLECTION,
        deadline=make_relative_deadline(datetime.timedelta(hours=1)),
    )
    transfer_request.add_item(SRC_PATH, DST_PATH)

This is then valid to submit with a :class:`TransferClient`:

.. code-block:: python

    tc = globus_sdk.TransferClient(...)

    tc.submit_transfer(transfer_request)

.. _userguide_transfer_relative_deadline_example:

Summary: Complete Example
-------------------------

For a complete example script, we will need to also include a
:class:`GlobusApp` for login, so that we can setup the :class:`TransferClient`
correctly.
We'll also take a small step to make the script work with mapped collections
which require the ``data_access`` scope, like the tutorial collections.
With those small additions, the above examples can be turned into a working
script!

*This example is complete. It should run without errors "as is".*

.. literalinclude:: submit_transfer_relative_deadline.py
    :caption: ``submit_transfer_relative_deadline.py`` [:download:`download <submit_transfer_relative_deadline.py>`]
    :language: python
