#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build and update audit rows from subtitle files and audit findings."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.subtitles import Series

from .decisions import ReviewDecisions
from .files import load_report_notes, load_review_output
from .models import AuditRow, AuditStatus

__all__ = ["apply_audit_findings", "build_audit_rows", "carry_audit_progress"]


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
    decisions: ReviewDecisions | None,
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
    texts, revision_notes = load_review_output(source, decisions, outfile_path)
    block_ranges = _get_block_ranges(source, decisions)
    block_numbers = {
        index: number
        for number, (first, last) in enumerate(block_ranges, 1)
        for index in range(first, last)
    }
    imported_notes = {}
    if report_path is not None:
        imported_notes = load_report_notes(report_path, len(source))
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
    source: Series, decisions: ReviewDecisions | None
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
