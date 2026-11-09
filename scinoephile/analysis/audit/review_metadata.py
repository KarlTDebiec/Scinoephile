#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Match logged review decisions to subtitle tracks for audit reports."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from scinoephile.core.llms import TestCase

__all__ = ["ReviewAuditMetadata", "get_review_metadata"]


@dataclass(frozen=True, kw_only=True)
class ReviewAuditMetadata:
    """Matched notes and verification state for one review decision log."""

    covered_indexes: frozenset[int]
    """Zero-based subtitle indexes covered by current logged cases."""
    notes_by_index: Mapping[int, tuple[str, ...]]
    """Current revision notes keyed by zero-based subtitle index."""
    unverified_indexes: frozenset[int]
    """Covered subtitle indexes belonging to unverified cases."""


def get_review_metadata(
    review_cases: Sequence[TestCase],
    original: tuple[str, ...],
    reviewed: tuple[str, ...],
) -> ReviewAuditMetadata:
    """Match the latest current review cases to subtitle text.

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
        query_texts, revised_texts, revision_by_index = _get_review_case_data(
            review_case
        )
        candidate_starts = [
            start
            for start in range(len(original) - len(query_texts) + 1)
            if original[start : start + len(query_texts)] == query_texts
        ]
        if not candidate_starts:
            # Persisted logs retain historical queries after their input changes
            continue

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
            for local_index, revision in revision_by_index.items():
                index = start + local_index - 1
                note = cast(str, revision["note"]).strip()
                notes = notes_by_index.setdefault(index, [])
                if note not in notes:
                    notes.append(note)

    return ReviewAuditMetadata(
        covered_indexes=frozenset(covered_indexes),
        notes_by_index={index: tuple(notes) for index, notes in notes_by_index.items()},
        unverified_indexes=frozenset(unverified_indexes),
    )


def _get_review_case_data(
    review_case: TestCase,
) -> tuple[tuple[str, ...], tuple[str, ...], dict[int, dict[str, int | str]]]:
    """Get query, reviewed, and revision data from a review test case.

    Arguments:
        review_case: deserialized review test case
    Returns:
        query texts, expected reviewed texts, and revisions keyed by local index
    """
    answer = review_case.answer
    query_subtitles = cast(
        list[dict[str, int | str]], review_case.query.model_dump()["subtitles"]
    )
    answer_revisions: list[dict[str, int | str]] = []
    if answer is not None:
        answer_revisions = cast(
            list[dict[str, int | str]], answer.model_dump()["revisions"]
        )
    query_texts = tuple(cast(str, subtitle["text"]) for subtitle in query_subtitles)
    revision_by_index = {
        cast(int, revision["index"]): revision for revision in answer_revisions
    }
    revised_texts_list = []
    for local_index, query_text in enumerate(query_texts, 1):
        revised_text = query_text
        if local_index in revision_by_index:
            revised_text = cast(str, revision_by_index[local_index]["text"])
        revised_texts_list.append(revised_text)
    revised_texts = tuple(revised_texts_list)
    return query_texts, revised_texts, revision_by_index
