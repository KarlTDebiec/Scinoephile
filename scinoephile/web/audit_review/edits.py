#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prepare manual edits to proofreading and audit rows."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from .decisions import ReviewDecisions
from .models import AuditRow, AuditStatus

__all__ = ["build_review_edit", "prepare_review_edit"]


def build_review_edit(
    current: AuditRow,
    *,
    reviewed: str,
    review_note: str,
    notes: str,
    finding: str,
    verified: bool,
) -> AuditRow:
    """Validate a submitted edit and normalize its subtitle line endings.

    Arguments:
        current: existing row whose subtitle and audit fields can be edited
        reviewed: corrected subtitle text
        review_note: explanation for changing the subtitle
        notes: independent audit explanation
        finding: submitted audit verdict
        verified: submitted human verification mark
    Returns:
        draft row containing the validated form values
    Raises:
        ValueError: if the subtitle, explanation, or verdict is invalid
    """
    reviewed = reviewed.replace("\r\n", "\n").replace("\r", "\n")
    if not reviewed.strip() or len(reviewed) > 1000 or "\n\n" in reviewed:
        raise ValueError(
            "Subtitle text must contain 1–1000 characters and no blank lines"
        )
    if reviewed != current.original and not review_note.strip():
        raise ValueError("A note is required for changed proofreading text")
    if len(review_note) > 1000:
        raise ValueError("Revision notes must not exceed 1000 characters")
    try:
        status = AuditStatus(finding)
    except ValueError as exc:
        raise ValueError("Unknown audit verdict") from exc
    status.validate_notes(notes)
    return replace(
        current,
        reviewed=reviewed,
        review_note=review_note,
        notes=notes,
        finding=status,
        verified=verified,
    )


def prepare_review_edit(
    rows: list[AuditRow],
    draft: AuditRow,
    decisions: ReviewDecisions | None,
    *,
    proofreading_changed: bool,
) -> tuple[list[AuditRow], ReviewDecisions | None, list[AuditRow]]:
    """Apply one edit and reset stale findings on changed subtitles.

    Arguments:
        rows: current editor rows in source order
        draft: validated edited row
        decisions: current native decision log, if configured
        proofreading_changed: whether the proofread output needs to be written
    Returns:
        candidate subtitle rows, native decisions, and affected audit rows
    """
    current = rows[draft.index - 1]
    updated = rows
    if proofreading_changed:
        updated, decisions = _apply_proofreading_edit(rows, current, draft, decisions)
    affected = {
        row.key: replace(row, verified=False, finding=AuditStatus.unaudited, notes="")
        for row in updated
        if row != rows[row.index - 1]
    }
    # Keep the reset unless the form also changed its audit decision
    if draft.key not in affected or (draft.notes, draft.finding, draft.verified) != (
        current.notes,
        current.finding,
        current.verified,
    ):
        affected[draft.key] = replace(
            updated[draft.index - 1],
            notes=draft.notes,
            finding=draft.finding,
            verified=draft.verified
            and (draft.key not in affected or not current.verified),
        )
    return (
        updated,
        decisions,
        [replace(row, version=row.version + 1) for row in affected.values()],
    )


def _apply_proofreading_edit(
    rows: list[AuditRow],
    current: AuditRow,
    draft: AuditRow,
    decisions: ReviewDecisions | None,
) -> tuple[list[AuditRow], ReviewDecisions | None]:
    """Apply edited text to the subtitle output and any native decisions.

    Arguments:
        rows: current text and audit progress
        current: row being saved
        draft: validated row with new subtitle text and explanation
        decisions: current native decision log, if configured
    Returns:
        candidate subtitle rows and optional native decision log
    Raises:
        ValueError: if starting a decision log would change existing subtitles
    """
    if decisions is None:
        updated = list(rows)
        updated[current.index - 1] = replace(
            current, reviewed=draft.reviewed, review_note=draft.review_note
        )
        return updated, None
    decisions = deepcopy(decisions)
    # Seed any existing output edits when starting a new JSON log
    if not decisions.cases:
        for row in rows:
            if row.changed:
                decisions.edit(row.index - 1, row.reviewed, row.review_note)
        seeded_texts, _ = decisions.render()
        if seeded_texts != [row.reviewed for row in rows]:
            raise ValueError(
                "Existing corrections differ across linked subtitles. "
                "Open the editor without --json to keep those corrections."
            )
    decisions.edit(draft.index - 1, draft.reviewed, draft.review_note)
    texts, revision_notes = decisions.render()
    return [
        replace(
            row,
            reviewed=texts[row.index - 1],
            review_note=revision_notes[row.index - 1],
            shared_indexes=decisions.shared_indexes(row.index - 1),
        )
        for row in rows
    ], decisions
