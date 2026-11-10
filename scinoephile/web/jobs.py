#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background job lifecycle and progress for local web workflows."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from logging import getLogger
from threading import RLock, Thread

__all__ = ["BackgroundJob", "BackgroundJobState"]

logger = getLogger(__name__)


@dataclass(frozen=True)
class BackgroundJobState:
    """Immutable progress for a background job."""

    status: str = "ready"
    """Ready, running, complete, or error."""
    completed: int = 0
    """Number of completed work units."""
    total: int = 0
    """Number of work units planned for the run."""
    error: str = ""
    """Latest failure message."""


class BackgroundJob[State: BackgroundJobState]:
    """Run background work and provide synchronized progress snapshots."""

    def __init__(self, state: State, *, thread_name: str):
        """Initialize a job before any work has started.

        Arguments:
            state: initial progress and workflow-specific state
            thread_name: name used for the worker thread and failure logs
        """
        self._state = state
        self._thread_name = thread_name
        self._lock = RLock()
        self._thread: Thread | None = None

    def snapshot(self) -> State:
        """Get the current progress and any workflow-specific state.

        Returns:
            immutable state captured under the job lock
        """
        with self._lock:
            return self._state

    def _advance(self):
        """Record one completed unit of work."""
        with self._lock:
            self._state = replace(self._state, completed=self._state.completed + 1)

    def _run_worker(self, work: Callable[[], None], release: Callable[[], None]):
        """Run the work, record its outcome, and release its reservation.

        Arguments:
            work: workflow to run in the worker thread
            release: callback that releases the workflow's reservation
        """
        status = "error"
        error = "Background job interrupted"
        try:
            work()
        except Exception as exc:
            logger.exception(f"{self._thread_name} failed")
            error = str(exc)
        else:
            status = "complete"
            error = ""
        finally:
            with self._lock:
                self._state = replace(self._state, status=status, error=error)
                release()

    def _start_worker(
        self,
        state: State,
        *,
        work: Callable[[], None],
        release: Callable[[], None],
        start_error: str,
    ):
        """Start a reserved run while the caller holds the job lock.

        Arguments:
            state: fresh progress and settings for the run
            work: workflow to run in the worker thread
            release: callback that releases the workflow's reservation
            start_error: message to retain if the worker fails to start
        Raises:
            RuntimeError: if the worker thread cannot start
        """
        self._state = replace(state, status="running")
        try:
            self._thread = Thread(
                target=self._run_worker,
                args=(work, release),
                daemon=True,
                name=self._thread_name,
            )
            self._thread.start()
        except Exception:
            self._thread = None
            self._state = replace(self._state, status="error", error=start_error)
            release()
            raise
