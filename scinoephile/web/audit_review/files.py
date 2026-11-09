#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""File I/O for the subtitle audit editor."""

from __future__ import annotations

import re
from copy import deepcopy
from hashlib import sha256
from html import unescape
from os import fsync
from pathlib import Path
from shutil import copy2
from tempfile import NamedTemporaryFile

from scinoephile.common.file import create_unique_directory, open_atomic_text_file
from scinoephile.core.subtitles import Series

from .decisions import ReviewDecisions
from .exceptions import InvalidReviewSubtitleError
from .models import AuditRow

__all__ = [
    "backup_review_files",
    "get_file_hashes",
    "load_report_notes",
    "load_review_output",
    "parse_source_srt",
    "restore_files",
    "validate_project_paths",
    "write_review_files",
]


def backup_review_files(outfile_path: Path, json_path: Path | None) -> Path:
    """Copy the existing proofreading output before a rerun.

    Arguments:
        outfile_path: current proofread SRT
        json_path: optional native proofreading decisions
    Returns:
        backup directory for the files and review database
    """
    backup_dir_path = create_unique_directory(
        parent_dir_path=outfile_path.parent,
        prefix=f"{outfile_path.stem}.before-reproofread-",
    )
    copy2(outfile_path, backup_dir_path / "proofread.srt")
    if json_path is not None and json_path.exists():
        copy2(json_path, backup_dir_path / "review.json")
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


def load_report_notes(file_path: Path, count: int) -> dict[int, str]:
    """Import only Notes from a generated audit table, never its rendered text.

    Arguments:
        file_path: existing Markdown audit report
        count: number of source subtitles
    Returns:
        independent notes keyed by one-based subtitle number
    Raises:
        ValueError: if the table is malformed, duplicated, or out of range
    """
    columns = []
    notes = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
        if cells and cells[0] == "Subtitle":
            columns = cells
            continue
        if not cells or not cells[0].isdigit():
            continue
        if len(cells) != len(columns) or "Notes" not in columns:
            raise ValueError("Audit report has no valid Notes column")
        index = int(cells[0])
        if not 1 <= index <= count or index in notes:
            raise ValueError("Audit report has duplicate or out-of-range row indexes")
        notes[index] = unescape(
            cells[columns.index("Notes")].replace("\\|", "|").replace("<br>", "\n")
        )
    if not notes:
        raise ValueError("Audit report contains no subtitle rows")
    return notes


def load_review_output(
    source: Series, decisions: ReviewDecisions | None, outfile_path: Path | None
) -> tuple[list[str], list[str]]:
    """Load output or native proposals and validate their correspondence.

    Arguments:
        source: original subtitle series
        decisions: native proofreading decisions, if configured
        outfile_path: optional proofread SRT to load
    Returns:
        editable output text and native revision explanations
    Raises:
        ValueError: if output timings or JSON answers disagree
    """
    texts = [s.text_with_newline for s in source]
    revision_notes = [""] * len(texts)
    if decisions is not None:
        texts, revision_notes = decisions.render()
    if outfile_path is not None and outfile_path.exists():
        output = Series.load(outfile_path)
        if [(s.start, s.end) for s in output] != [(s.start, s.end) for s in source]:
            raise ValueError("Original and output subtitle timings must match")
        output_texts = [s.text_with_newline for s in output]
        if decisions is not None and decisions.cases:
            if output_texts != texts:
                raise ValueError("Output subtitles disagree with the review JSON")
        else:
            texts = output_texts
    return texts, revision_notes


def parse_source_srt(content: bytes) -> Series:
    """Read source subtitles from the captured SRT bytes.

    Arguments:
        content: original SRT encoded in UTF-8, optionally with a BOM
    Returns:
        parsed subtitle series
    """
    text = content.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return Series.from_string(text, format_="srt")


def restore_files(originals: dict[Path, bytes | None]):
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


def validate_project_paths(
    infile_path: Path,
    outfile_path: Path,
    state_path: Path,
    *,
    json_path: Path | None,
    report_path: Path | None,
):
    """Require distinct subtitle, JSON, progress and optional report files.

    Arguments:
        infile_path: original subtitle path
        outfile_path: proofread subtitle path
        state_path: audit progress database path
        json_path: optional native proofreading decisions path
        report_path: optional read-only report path
    Raises:
        ValueError: if paths collide or the output is not an SRT
    """
    paths = [infile_path, outfile_path, state_path]
    if json_path is not None:
        paths.append(json_path)
    if report_path is not None:
        paths.append(report_path)
    if len(set(paths)) != len(paths):
        raise ValueError("Input, output, JSON, progress and report paths must differ")
    for index, left_path in enumerate(paths):
        for right_path in paths[index + 1 :]:
            if (
                left_path.exists()
                and right_path.exists()
                and left_path.samefile(right_path)
            ):
                raise ValueError("Input and writable files must not alias each other")
    if outfile_path.suffix.lower() != ".srt":
        raise ValueError("The edited subtitle output must be an SRT file")


def write_review_files(
    source: Series,
    rows: list[AuditRow],
    outfile_path: Path,
    *,
    decisions: ReviewDecisions | None,
    json_path: Path | None,
) -> dict[Path, bytes | None]:
    """Replace each output atomically and restore files on an I/O failure.

    Arguments:
        source: original subtitle series for the output
        rows: validated final subtitle rows
        outfile_path: proofread subtitle output
        decisions: candidate native JSON decisions
        json_path: optional destination for the native decisions
    Returns:
        original file contents for rollback if the database commit fails
    Raises:
        ValueError: if the output cannot round-trip through SRT
        BaseException: if writing fails, after restoring replaced files
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
    writes = {outfile_path: content}
    if decisions is not None and json_path is not None:
        writes[json_path] = decisions.serialize()
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
        restore_files({p: originals[p] for p in reversed(written)})
        raise
    return originals
