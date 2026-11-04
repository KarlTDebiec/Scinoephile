#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose functions for file interaction and manipulation."""

from __future__ import annotations

import sys
from collections.abc import Generator
from contextlib import contextmanager
from errno import EACCES, EAGAIN, EDEADLK
from logging import getLogger
from math import isfinite
from os import fsync, remove
from pathlib import Path
from shutil import move, rmtree
from tempfile import NamedTemporaryFile, mkdtemp
from time import monotonic, sleep
from typing import TextIO, cast

__all__ = [
    "file_lock",
    "get_temp_directory_path",
    "get_temp_file_path",
    "open_atomic_text_file",
    "rename_preexisting_output_path",
]

logger = getLogger(__name__)


@contextmanager
def file_lock(  # noqa: PLR0912
    file_path: Path, *, timeout: float = 5.0
) -> Generator[None]:
    """Hold an exclusive OS file lock with a bounded wait for competing writers.

    Every writer must use the same lock file for the entire read-modify-write
    operation. The file remains on disk and must not be replaced or unlinked while
    writers can use it. Closing the handle releases the lock, including after a crash.
    Acquisition is not reentrant, even within one process.

    Arguments:
        file_path: persistent lock file, with parent directories created as needed
        timeout: maximum acquisition wait in seconds; zero fails immediately if held
    Yields:
        control while the exclusive lock is held
    Raises:
        BlockingIOError: if another writer holds the lock beyond the timeout
        OSError: if opening, locking, or unlocking the file fails
        ValueError: if timeout is negative or nonfinite
    """
    if not isfinite(timeout):
        raise ValueError("File lock timeout must be finite.")
    if timeout < 0:
        raise ValueError("File lock timeout must not be negative.")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a+b") as handle:
        if sys.platform == "win32":
            import msvcrt  # noqa: PLC0415

            if file_path.stat().st_size == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
        else:
            import fcntl  # noqa: PLC0415

        deadline = monotonic() + timeout
        while True:
            try:
                if sys.platform == "win32":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno not in {EACCES, EAGAIN, EDEADLK}:
                    raise
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise BlockingIOError(f"File lock is held: {file_path}") from exc
                sleep(min(0.05, remaining))
            else:
                break
        try:
            yield
        finally:
            if sys.platform == "win32":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def get_temp_directory_path(
    *, parent_dir_path: Path | None = None, prefix: str | None = None
) -> Generator[Path]:
    """Provide path to a temporary directory and remove it once no longer needed.

    Arguments:
        parent_dir_path: parent directory, defaulting to the system temporary directory
        prefix: directory name prefix, defaulting to the system temporary prefix
    Yields:
        path to temporary directory
    """
    temp_directory_path = None
    try:
        temp_directory_path = Path(
            mkdtemp(dir=parent_dir_path, prefix=prefix)
        ).resolve()
        yield temp_directory_path
    finally:
        if temp_directory_path:
            rmtree(temp_directory_path)


@contextmanager
def get_temp_file_path(suffix: str | None = None) -> Generator[Path]:
    """Provide path to a temporary file and remove it once no longer needed.

    Arguments:
        suffix: suffix of named temporary file
    Yields:
        path to temporary file
    """
    temp_file_path = None
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        temp_file_path = Path(temp_file.name)
        remove(temp_file_path)
        yield temp_file_path
    finally:
        if temp_file_path and temp_file_path.exists():
            try:
                remove(temp_file_path)
            except PermissionError as exc:
                logger.debug(
                    f"temp_file_path encountered PermissionException '{exc}'; "
                    f"temporary file {temp_file_path}, will not be removed."
                )


@contextmanager
def open_atomic_text_file(
    output_path: Path, *, encoding: str = "utf-8"
) -> Generator[TextIO]:
    """Open a temporary text file that atomically replaces an output on success.

    The temporary file is created beside the output so replacement remains on the
    same filesystem. It is flushed and synchronized before replacement, and removed
    if writing fails.

    Arguments:
        output_path: path to replace after writing succeeds
        encoding: text encoding
    Yields:
        writable temporary text file
    Raises:
        BaseException: if the operation fails
    """
    temp_file = NamedTemporaryFile(
        "w",
        delete=False,
        dir=output_path.parent,
        encoding=encoding,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_file.name)
    try:
        with temp_file:
            yield cast(TextIO, temp_file)
            temp_file.flush()
            fsync(temp_file.fileno())
        temp_path.replace(output_path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def rename_preexisting_output_path(output_path: Path):
    """Check if a proposed output file exists, and if so rename the existing file.

    Arguments:
        output_path: Path to proposed output file
    """
    output_path = output_path.resolve()
    if output_path.exists():
        backup_i = 0
        while True:
            backup_path = output_path.with_stem(f"{output_path.stem}_{backup_i:03d}")
            if not backup_path.exists():
                logger.info(f"Moving pre-existing file {output_path} to {backup_path}")
                move(output_path, backup_path)
                break
            backup_i += 1
