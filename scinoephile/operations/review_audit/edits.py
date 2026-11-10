#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prepare manual edits to proofreading and audit rows."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from .proofreading_decisions import ProofreadingDecisions
from .rows import AuditRow, AuditStatus

__all__ = ["build_review_edit", "prepare_proofreading_edit"]


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
    if status == AuditStatus.unaudited and notes.strip():
        raise ValueError("Choose an audit verdict before saving an audit note")
    return replace(
        current,
        reviewed=reviewed,
        review_note=review_note,
        notes=notes,
        finding=status,
        verified=verified,
    )


def prepare_proofreading_edit(
    rows: list[AuditRow], draft: AuditRow, decisions: ProofreadingDecisions
) -> tuple[list[AuditRow], ProofreadingDecisions]:
    """Apply the edited text to a copy of the native proofreading decisions.

    Arguments:
        rows: current editor rows in source order
        draft: validated edited row
        decisions: current native decision log
    Returns:
        candidate subtitle rows and proofreading decisions
    """
    decisions = deepcopy(decisions)
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
