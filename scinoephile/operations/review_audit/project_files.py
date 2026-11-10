#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""File I/O, locking, and coordinated writes for a review audit project."""

from __future__ import annotations

import sys
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from hashlib import sha256
from os import fsync
from pathlib import Path
from shutil import copy2
from tempfile import NamedTemporaryFile

from scinoephile.common.file import create_temp_directory, open_atomic_text_file
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series

from .exceptions import InvalidReviewSubtitleError
from .proofreading_decisions import ProofreadingDecisions
from .rows import AuditRow

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

__all__ = [
    "backup_review_files",
    "get_file_hashes",
    "lock_review_files",
    "render_review_files",
    "write_files",
]


def backup_review_files(
    outfile_path: Path, proofreading_json_path: Path, audit_json_path: Path
) -> Path:
    """Copy the existing proofreading output before a rerun.

    Arguments:
        outfile_path: current proofread SRT
        proofreading_json_path: native proofreading decisions
        audit_json_path: audit test-case file
    Returns:
        backup directory containing the previous project files
    """
    backup_dir_path = create_temp_directory(
        parent_dir_path=outfile_path.parent,
        prefix=f"{outfile_path.stem}.before-reproofread-",
    )
    copy2(outfile_path, backup_dir_path / "proofread.srt")
    if proofreading_json_path.exists():
        copy2(proofreading_json_path, backup_dir_path / "review.json")
    copy2(audit_json_path, backup_dir_path / "audit.json")
    return backup_dir_path


def get_file_hashes(*file_paths: Path | None) -> tuple[bytes | None, ...]:
    """Hash source and writable files to reject external edits on save.

    Arguments:
        *file_paths: files in the order to hash them
    Returns:
        SHA-256 hashes, with None for absent files
    """
    hashes = []
    for file_path in file_paths:
        file_hash = None
        if file_path is not None and file_path.exists():
            file_hash = sha256(file_path.read_bytes()).digest()
        hashes.append(file_hash)
    return tuple(hashes)


@contextmanager
def lock_review_files(lock_path: Path) -> Generator[None]:
    """Lock a review project across processes while loading or committing files.

    The lock file stays in place so waiting sessions share the same file.

    Arguments:
        lock_path: lock file beside the proofread subtitle output
    Yields:
        control while holding the exclusive project lock
    Raises:
        ScinoephileError: if the lock cannot be acquired
    """
    with ExitStack() as stack:
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            handle = stack.enter_context(lock_path.open("a+b"))
            if sys.platform == "win32":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except OSError as exc:
            raise ScinoephileError(
                f"Unable to lock review project {lock_path}: {exc}"
            ) from exc
        yield


def render_review_files(
    source: Series,
    rows: list[AuditRow],
    outfile_path: Path,
    *,
    decisions: ProofreadingDecisions,
    proofreading_json_path: Path,
) -> dict[Path, str]:
    """Serialize subtitle output and native decisions before replacing files.

    Arguments:
        source: original subtitle series for the output
        rows: validated final subtitle rows
        outfile_path: proofread subtitle output
        decisions: candidate native JSON decisions
        proofreading_json_path: destination for the native decisions
    Returns:
        candidate contents keyed by output path
    Raises:
        ValueError: if the output cannot round-trip through SRT
    """
    output = deepcopy(source)
    for subtitle, row in zip(output, rows, strict=True):
        subtitle.text = row.reviewed.replace("\n", "\\N")
    content = output.to_string("srt")
    reloaded = Series.from_string(content, format_="srt")
    if [(s.start, s.end, s.text_with_newline) for s in reloaded] != [
        (row.start, row.end, row.reviewed) for row in rows
    ]:
        raise InvalidReviewSubtitleError(
            "Subtitle text cannot be saved unchanged in SRT. "
            "Remove leading or trailing whitespace and SRT control sequences."
        )
    return {outfile_path: content, proofreading_json_path: decisions.serialize()}


def write_files(writes: dict[Path, str]):
    """Replace each output atomically and restore files on a write failure.

    Arguments:
        writes: new contents keyed by destination path
    Raises:
        BaseException: if writing fails, after restoring replaced files
    """
    originals: dict[Path, bytes | None] = {p: None for p in writes}
    for file_path in writes:
        if file_path.exists():
            originals[file_path] = file_path.read_bytes()
    written = []
    try:
        for file_path, content in writes.items():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open_atomic_text_file(file_path) as handle:
                handle.write(content)
            written.append(file_path)
    except BaseException:
        _restore_files({p: originals[p] for p in reversed(written)})
        raise


def _restore_files(originals: dict[Path, bytes | None]):
    """Restore replaced files byte-for-byte after a failed save.

    Arguments:
        originals: old file bytes, or None for newly created outputs
    Raises:
        OSError: if restoring a file fails
    """
    for file_path, original in originals.items():
        if original is None:
            file_path.unlink(missing_ok=True)
            continue
        with NamedTemporaryFile("wb", dir=file_path.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            try:
                handle.write(original)
                handle.flush()
                fsync(handle.fileno())
            except BaseException:
                handle.close()
                temp_path.unlink(missing_ok=True)
                raise
        try:
            temp_path.replace(file_path)
        finally:
            temp_path.unlink(missing_ok=True)
