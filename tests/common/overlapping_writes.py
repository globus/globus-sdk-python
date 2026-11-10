"""
Helpers for tests which need two writers to overlap in one precise order,
such as tests of how writes interact with process-wide state (like the umask).

The order is enforced with events rather than sleeps, so it is the same on every run,
and it does not depend on how the code under test is implemented.
"""

from __future__ import annotations

import contextlib
import os
import sqlite3
import threading
import typing as t


def current_umask() -> int:
    """Read the process umask. (`os.umask` can only be read by setting it.)"""
    current = os.umask(0)
    os.umask(current)
    return current


@contextlib.contextmanager
def process_umask(value: int) -> t.Iterator[None]:
    """Set the process umask for the duration of a block, then restore it."""
    original = os.umask(value)
    try:
        yield
    finally:
        os.umask(original)


class OverlappingWrites:
    """
    Run two writes in separate threads, in this order::

        first starts -> second starts -> first finishes -> second finishes

    Each write must call its checkpoint (``first_checkpoint`` or ``second_checkpoint``)
    at a point where the code under test is mid-write.
    The first write waits at its checkpoint until the second is also at its checkpoint.
    The second write waits at its checkpoint until the first has completely finished.

    If the code under test serializes the writes, the second can never reach its
    checkpoint while the first waits, so the first simply times out and carries on.
    The order of events is then different, but nothing deadlocks.

    Usage
    -----

    An ``OverlappingWrites`` object is used once, and its lifecycle wraps
    around the code under test: build the writes with its checkpoints,
    then hand them to ``run()``, which starts and orders the threads.

    .. code-block:: python

        controller = OverlappingWrites()
        action1 = build_action1(callback=controller.first_checkpoint)
        action2 = build_action2(callback=controller.second_checkpoint)
        controller.run(action1, action2)

        # now assert on the state left behind by the overlapping writes

    ``run()`` waits for both threads, raises the first exception that either raised,
    and fails if either write never reached its checkpoint.
    """

    def __init__(self, timeout: float = 0.2) -> None:
        self._timeout = timeout
        self._first_started = threading.Event()
        self._second_started = threading.Event()
        self._first_finished = threading.Event()

    def first_checkpoint(self) -> None:
        self._first_started.set()
        self._second_started.wait(self._timeout)

    def second_checkpoint(self) -> None:
        self._second_started.set()
        self._first_finished.wait(self._timeout)

    def run(self, first: t.Callable[[], t.Any], second: t.Callable[[], t.Any]) -> None:
        errors: list[Exception] = []

        def run_first() -> None:
            try:
                first()
            except Exception as e:
                errors.append(e)
            finally:
                self._first_finished.set()

        def run_second() -> None:
            try:
                second()
            except Exception as e:
                errors.append(e)

        first_thread = threading.Thread(target=run_first)
        second_thread = threading.Thread(target=run_second)

        first_thread.start()
        assert self._first_started.wait(
            5
        ), "the first write never reached its checkpoint"
        second_thread.start()
        first_thread.join(5)
        second_thread.join(5)

        assert not (first_thread.is_alive() or second_thread.is_alive())
        assert (
            self._second_started.is_set()
        ), "the second write never reached its checkpoint"
        if errors:
            raise errors[0]


class CheckpointDict(dict[str, t.Any]):
    """
    A dict which calls a checkpoint when it is iterated.

    When this is stored as token data, ``json.dump`` iterates it while writing, which
    is after the file has been opened.
    """

    def __init__(
        self, checkpoint: t.Callable[[], None], data: dict[str, t.Any]
    ) -> None:
        super().__init__(data)
        self._checkpoint = checkpoint

    def items(self) -> t.Any:
        self._checkpoint()
        return super().items()


def sqlite_factory_with_checkpoint(
    checkpoint: t.Callable[[], None],
) -> t.Callable[..., sqlite3.Connection]:
    """
    A ``factory`` for ``sqlite3.connect()`` which calls a checkpoint just before the
    database file is opened (and therefore just before it is created).
    """

    def factory(*args: t.Any, **kwargs: t.Any) -> sqlite3.Connection:
        checkpoint()
        return sqlite3.Connection(*args, **kwargs)

    return factory
