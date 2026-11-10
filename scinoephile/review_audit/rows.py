#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build and update audit rows from subtitle files and audit findings."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from html import unescape
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.subtitles import Series

from .proofreading_decisions import ProofreadingDecisions

__all__ = [
    "AuditRow",
    "AuditStatus",
    "apply_audit_findings",
    "build_audit_rows",
    "carry_audit_progress",
]


class AuditStatus(StrEnum):
    """Explicit verdict for an independent proofreading audit."""

    unaudited = "unaudited"
    """No audit verdict has been recorded."""
    review = "review"
    """The subtitle needs human review."""
    ok = "ok"
    """The audit found no issue."""

    def validate_notes(self, notes: str):
        """Require an explanation for a Review verdict and empty notes for OK.

        Arguments:
            notes: independent audit explanation
        Raises:
            ValueError: if the notes contradict the verdict
        """
        if self is AuditStatus.review and not notes.strip():
            raise ValueError("Audit notes are required when audit status is Review")
        if self is AuditStatus.ok and notes:
            raise ValueError("Clear audit notes when audit status is OK")


@dataclass(frozen=True)
class AuditRow:
    """A subtitle pair, provenance, and its independent human audit state."""

    key: str
    """Content identity; changed inputs get fresh audit progress."""
    track_id: str
    """Track identifier."""
    label: str
    """Track display label."""
    language: str
    """Subtitle language tag."""
    index: int
    """One-based subtitle number."""
    start: int
    """Start time in milliseconds."""
    end: int
    """End time in milliseconds."""
    original: str
    """Validated source text."""
    reviewed: str
    """Proposed proofread text."""
    review_note: str
    """Read-only model explanation."""
    notes: str
    """Independent audit notes."""
    finding: AuditStatus = AuditStatus.unaudited
    """Independent audit verdict."""
    verified: bool = False
    """Human audit progress, independent of proofreading JSON verification."""
    version: int = 0
    """Optimistic concurrency version."""

    shared_indexes: tuple[int, ...] = ()
    """One-based subtitle indexes sharing this JSON decision."""

    block_number: int = 0
    """Stable one-based proofreading block number."""

    @property
    def changed(self) -> bool:
        """Whether proofreading changed this subtitle."""
        return self.original != self.reviewed


def apply_audit_findings(
    rows: list[AuditRow],
    block: tuple[AuditRow, ...],
    findings: dict[int, tuple[str, str]],
    *,
    rerun: bool,
) -> list[AuditRow]:
    """Apply automated findings to a reserved block.

    Arguments:
        rows: current editor rows
        block: reserved context rows supplied to the auditor
        findings: verdict and note for each one-based index in the block
        rerun: replace existing findings while retaining human verification
    Returns:
        candidate audit rows with new findings and versions
    Raises:
        ValueError: if the block changed or findings are incomplete or invalid
    """
    if set(findings) != {row.index for row in block}:
        raise ValueError("Audit findings must cover the complete block")
    current = {row.key: row for row in rows}
    updated = []
    for row in block:
        if not rerun and (row.verified or row.finding != AuditStatus.unaudited):
            continue
        if current[row.key] != row:
            raise ValueError("Subtitle changed during auditing")
        status, note = findings[row.index]
        if status not in {AuditStatus.ok, AuditStatus.review}:
            raise ValueError("Invalid automated audit verdict")
        note = note.strip()
        if (status == AuditStatus.review) != bool(note):
            raise ValueError("Only Review verdicts require audit notes")
        updated.append(
            replace(
                row, notes=note, finding=AuditStatus(status), version=row.version + 1
            )
        )
    return updated


def build_audit_rows(
    source: Series,
    source_content: bytes,
    language: Language,
    decisions: ProofreadingDecisions | None,
    *,
    outfile_path: Path | None = None,
    report_path: Path | None = None,
) -> tuple[list[AuditRow], list[tuple[int, int]]]:
    """Build a baseline for an opened or newly proofread project.

    Arguments:
        source: original subtitle series
        source_content: original SRT bytes used to identify the baseline
        language: proofreading language
        decisions: native proofreading decisions, if configured
        outfile_path: existing proofread SRT to load when opening a project
        report_path: optional audit report used to seed findings and notes
    Returns:
        baseline rows and their nonoverlapping subtitle block ranges
    """
    texts, revision_notes = _load_review_output(source, decisions, outfile_path)
    block_ranges = _get_block_ranges(source, decisions)
    block_numbers = {
        index: number
        for number, (first, last) in enumerate(block_ranges, 1)
        for index in range(first, last)
    }
    imported_notes = {}
    if report_path is not None:
        imported_notes = _load_report_notes(report_path, len(source))
    label = language.code
    if language == Language.eng:
        label = "English"
    source_digest = sha256(source_content).hexdigest()

    rows = []
    for index, subtitle in enumerate(source.events):
        note = imported_notes.get(index + 1, "")
        finding = AuditStatus.unaudited
        if note == "OK":
            finding = AuditStatus.ok
            note = ""
        elif note.startswith(("Review;", "Incorrect;", "Check;")):
            finding = AuditStatus.review
        shared = (index + 1,)
        if decisions is not None:
            shared = decisions.shared_indexes(index)
        key = sha256(f"{source_digest}:{language.code}:{index}".encode()).hexdigest()
        rows.append(
            AuditRow(
                key=key,
                track_id=language.code,
                label=label,
                language=language.code,
                index=index + 1,
                start=subtitle.start,
                end=subtitle.end,
                original=subtitle.text_with_newline,
                reviewed=texts[index],
                review_note=revision_notes[index],
                notes=note,
                finding=finding,
                shared_indexes=shared,
                block_number=block_numbers[index],
            )
        )
    return rows, block_ranges


def carry_audit_progress(
    previous: list[AuditRow], updated: list[AuditRow]
) -> list[AuditRow]:
    """Carry findings forward after re-proofreading when the audited text matches.

    Arguments:
        previous: rows from the previously published baseline
        updated: rows from the new proofreading output, in the same order
    Returns:
        replacement rows with incremented versions and applicable audit progress
    """
    rows = []
    for old, replacement in zip(previous, updated, strict=True):
        current = replace(replacement, version=old.version + 1)
        if (
            current.original == old.original
            and current.reviewed == old.reviewed
            and current.review_note == old.review_note
        ):
            current = replace(
                current, finding=old.finding, notes=old.notes, verified=old.verified
            )
        rows.append(current)
    return rows


def _get_block_ranges(
    source: Series, decisions: ProofreadingDecisions | None
) -> list[tuple[int, int]]:
    """Use logged query boundaries or group the remaining subtitles by pauses.

    Arguments:
        source: original subtitle series
        decisions: native proofreading decisions, if configured
    Returns:
        nonoverlapping zero-based inclusive/exclusive subtitle ranges
    """
    count = len(source)
    if not count:
        return []
    joined = [False] * (count - 1)
    covered = set()
    if decisions is not None:
        for case_index, starts in decisions.locations.items():
            size = len(decisions.cases[case_index].query.subtitles)
            for first in starts:
                covered.update(range(first, first + size))
                for index in range(first, first + size - 1):
                    joined[index] = True
    for first, last in Series.get_block_indexes_by_pause(source):
        for index in range(first, last - 1):
            if index not in covered and index + 1 not in covered:
                joined[index] = True
    boundaries = [0]
    boundaries.extend(index + 1 for index, value in enumerate(joined) if not value)
    boundaries.append(count)
    return list(zip(boundaries[:-1], boundaries[1:], strict=True))


def _load_report_notes(file_path: Path, count: int) -> dict[int, str]:
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


def _load_review_output(
    source: Series, decisions: ProofreadingDecisions | None, outfile_path: Path | None
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
