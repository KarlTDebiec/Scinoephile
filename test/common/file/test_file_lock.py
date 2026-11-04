#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of persistent file lock ownership and bounded acquisition."""

from __future__ import annotations

from pathlib import Path
from time import monotonic

from pytest import raises

from scinoephile.common.file import file_lock
from test.helpers import parametrize


def test_file_lock_rejects_negative_timeout(tmp_path: Path):
    """Reject invalid waits before creating the lock file.

    Arguments:
        tmp_path: temporary directory for the lock
    """
    lock_path = tmp_path / "writer.lock"
    with raises(ValueError, match="must not be negative"):
        with file_lock(lock_path, timeout=-1):
            pass
    assert not lock_path.exists()


@parametrize("timeout", [float("nan"), float("inf"), float("-inf")])
def test_file_lock_rejects_nonfinite_timeout(tmp_path: Path, timeout: float):
    """Reject unbounded waits before creating any lock directory or file.

    Arguments:
        tmp_path: temporary directory for the lock
        timeout: nonfinite acquisition timeout
    """
    lock_path = tmp_path / "data/writer.lock"
    with raises(ValueError, match="must be finite"):
        with file_lock(lock_path, timeout=timeout):
            pass
    assert not lock_path.parent.exists()


def test_file_lock_releases_after_failure(tmp_path: Path):
    """Release ownership after a failed guarded operation without unlinking the lock.

    Arguments:
        tmp_path: temporary directory for the lock
    Raises:
        RuntimeError: if the guarded operation fails
    """
    lock_path = tmp_path / "data/writer.lock"
    with raises(RuntimeError, match="write failed"):
        with file_lock(lock_path):
            raise RuntimeError("write failed")
    assert lock_path.is_file()
    with file_lock(lock_path, timeout=0):
        assert lock_path.is_file()


def test_file_lock_wait_is_bounded(tmp_path: Path):
    """Prevent competing handles from entering the guarded operation.

    Arguments:
        tmp_path: temporary directory for the lock
    """
    lock_path = tmp_path / "writer.lock"
    with file_lock(lock_path):
        start_time = monotonic()
        with raises(BlockingIOError, match="File lock is held"):
            with file_lock(lock_path, timeout=0.1):
                pass
        assert 0.08 <= monotonic() - start_time < 1.0
    with file_lock(lock_path, timeout=0):
        pass
