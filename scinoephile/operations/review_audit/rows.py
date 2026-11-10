#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build and update audit rows from subtitle files and audit findings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from scinoephile.core import Language
from scinoephile.core.subtitles import Series

from .proofreading_decisions import ProofreadingDecisions

__all__ = ["AuditRow", "AuditStatus", "build_audit_rows"]


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
    """Whether the audit test case has been verified by a human."""
    proofreading_verified: bool = False
    """Whether the proofreading test cases covering this row are verified."""
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


def build_audit_rows(
    source: Series,
    source_hash: bytes,
    language: Language,
    decisions: ProofreadingDecisions,
) -> tuple[list[AuditRow], list[tuple[int, int]]]:
    """Build a baseline for an opened or newly proofread project.

    Arguments:
        source: original subtitle series
        source_hash: hash of the original SRT used to identify the baseline
        language: proofreading language
        decisions: native proofreading decisions
    Returns:
        baseline rows and their nonoverlapping subtitle block ranges
    """
    texts, revision_notes = decisions.render()
    block_ranges = decisions.block_ranges
    block_numbers = {
        index: number
        for number, (first, last) in enumerate(block_ranges, 1)
        for index in range(first, last)
    }
    source_digest = source_hash.hex()
    verified = decisions.verified_indexes()

    rows = []
    for index, subtitle in enumerate(source.events):
        key = sha256(f"{source_digest}:{language.code}:{index}".encode()).hexdigest()
        rows.append(
            AuditRow(
                key=key,
                language=language.code,
                index=index + 1,
                start=subtitle.start,
                end=subtitle.end,
                original=subtitle.text_with_newline,
                reviewed=texts[index],
                review_note=revision_notes[index],
                notes="",
                proofreading_verified=index in verified,
                shared_indexes=decisions.shared_indexes(index),
                block_number=block_numbers[index],
            )
        )
    return rows, block_ranges
