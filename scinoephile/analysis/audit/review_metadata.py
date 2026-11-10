#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Match logged review decisions to subtitle tracks for audit reports."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from scinoephile.core.llms import AnnotatedTestCaseSubtitle
from scinoephile.llms.review import ReviewTestCase

__all__ = ["ReviewAuditMetadata", "get_review_audit_metadata"]


@dataclass(frozen=True, kw_only=True)
class ReviewAuditMetadata:
    """Matched notes and verification state for one review decision log."""

    covered_indexes: frozenset[int]
    """Zero-based subtitle indexes covered by current logged cases."""
    notes_by_index: Mapping[int, tuple[str, ...]]
    """Current revision notes keyed by zero-based subtitle index."""
    unverified_indexes: frozenset[int]
    """Covered subtitle indexes belonging to unverified cases."""


def get_review_audit_metadata(
    review_cases: Sequence[ReviewTestCase],
    original: tuple[str, ...],
    reviewed: tuple[str, ...],
) -> ReviewAuditMetadata:
    """Match the latest answer for each query to the original and reviewed subtitles.

    Arguments:
        review_cases: deserialized review test cases
        original: original subtitle text
        reviewed: reviewed subtitle text
    Returns:
        current notes and verification metadata
    Raises:
        ValueError: if a current query's answer does not match reviewed subtitles
    """
    # Retain the latest logged decision for each deduplicated query
    latest_cases_by_query = {
        review_case.query.key: (case_index, review_case)
        for case_index, review_case in enumerate(review_cases, 1)
    }

    # Match current cases once and derive all report metadata together
    covered_indexes: set[int] = set()
    notes_by_index: dict[int, list[str]] = {}
    unverified_indexes: set[int] = set()
    for case_index, review_case in latest_cases_by_query.values():
        query_texts = tuple(subtitle.text for subtitle in review_case.query.subtitles)
        candidate_starts = [
            start
            for start in range(len(original) - len(query_texts) + 1)
            if original[start : start + len(query_texts)] == query_texts
        ]
        if not candidate_starts:
            # Persisted logs retain historical queries after their input changes
            continue

        revisions: Sequence[AnnotatedTestCaseSubtitle] = ()
        if review_case.answer is not None:
            revisions = review_case.answer.revisions
        expected_texts = list(query_texts)
        for revision in revisions:
            expected_texts[revision.index - 1] = revision.text
        revised_texts = tuple(expected_texts)

        matched_starts = [
            start
            for start in candidate_starts
            if reviewed[start : start + len(revised_texts)] == revised_texts
        ]
        if not matched_starts:
            raise ValueError(
                f"Review test case {case_index} does not match its subtitle pair"
            )

        for start in matched_starts:
            matched_indexes = set(range(start, start + len(query_texts)))
            covered_indexes.update(matched_indexes)
            if not review_case.verified:
                unverified_indexes.update(matched_indexes)
            for revision in revisions:
                index = start + revision.index - 1
                note = revision.note.strip()
                notes = notes_by_index.setdefault(index, [])
                if note not in notes:
                    notes.append(note)

    return ReviewAuditMetadata(
        covered_indexes=frozenset(covered_indexes),
        notes_by_index={index: tuple(notes) for index, notes in notes_by_index.items()},
        unverified_indexes=frozenset(unverified_indexes),
    )
