#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit guided subtitle review decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_groups
from scinoephile.llms.guided_review import GuidedReviewTestCase

__all__ = [
    "GuidedReviewAuditFilter",
    "audit_guided_review",
]


@dataclass(frozen=True, kw_only=True)
class _GuidedReviewBlock:
    """One target and guide block available for guided review."""

    block_number: int
    """One-based position in the complete block alignment."""
    target_indexes: tuple[int, ...]
    """One-based target subtitle indexes in the block."""
    target_texts: tuple[str, ...]
    """Target subtitle texts in the block."""
    guide_texts: tuple[str, ...]
    """Guide subtitle texts in the block."""
    aligned_guide_texts: tuple[tuple[str, ...], ...]
    """Timing-aligned guide texts for each target subtitle."""


class GuidedReviewAuditFilter(StrEnum):
    """Row filters supported by a guided-review audit."""

    all = "all"
    """Include every target subtitle from logged guided-review cases."""

    changes = "changes"
    """Include only target subtitles with revisions."""

    unverified = "unverified"
    """Include only target subtitles from cases not marked as verified."""


def audit_guided_review(
    target: Series,
    guide: Series,
    test_cases: Sequence[GuidedReviewTestCase],
    *,
    row_filter: GuidedReviewAuditFilter = GuidedReviewAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit logged guided-review decisions by target subtitle.

    Arguments:
        target: target subtitle series provided for guided review
        guide: guide subtitle series provided for guided review
        test_cases: logged guided-review test cases
        row_filter: row status filter
        first_index: first 1-indexed target subtitle number to include
        last_index: last 1-indexed target subtitle number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged case cannot be matched uniquely to source data
    """
    blocks_by_key = _get_blocks_by_key(target, guide)
    rows: list[tuple[int, int, str]] = []
    revised_subtitles = 0
    unchanged_subtitles = 0
    verified_subtitles = 0
    unverified_subtitles = 0
    subtitles = 0

    for test_case_index, test_case in enumerate(test_cases, 1):
        block = _get_test_case_block(
            test_case,
            blocks_by_key,
            test_case_index=test_case_index,
        )
        answer = test_case.answer
        revisions_by_index = (
            {revision.index: revision for revision in answer.revisions}
            if answer is not None
            else {}
        )

        for local_index, (subtitle_index, target_text, guide_texts) in enumerate(
            zip(
                block.target_indexes,
                block.target_texts,
                block.aligned_guide_texts,
                strict=True,
            ),
            1,
        ):
            if (first_index is not None and subtitle_index < first_index) or (
                last_index is not None and subtitle_index > last_index
            ):
                continue

            subtitles += 1
            revision = revisions_by_index.get(local_index)
            if revision is None:
                unchanged_subtitles += 1
            else:
                revised_subtitles += 1
            if test_case.verified:
                verified_subtitles += 1
            else:
                unverified_subtitles += 1

            if (row_filter is GuidedReviewAuditFilter.changes and revision is None) or (
                row_filter is GuidedReviewAuditFilter.unverified and test_case.verified
            ):
                continue

            target_revision = target_text
            if revision is not None:
                target_revision = f"{target_text}\n{revision.text}"

            cells = (
                str(subtitle_index),
                _format_texts(guide_texts),
                target_revision,
                "",
            )
            rows.append(
                (
                    subtitle_index,
                    test_case_index,
                    f"| {' | '.join(_escape_cell(cell) for cell in cells)} |",
                )
            )

    rows.sort(key=lambda item: (item[0], item[1]))
    lines = [
        "# Guided Subtitle Review Audit",
        "",
        "## Summary",
        "",
        f"- subtitles: {subtitles}",
        f"- revised subtitles: {revised_subtitles}",
        f"- unchanged subtitles: {unchanged_subtitles}",
        f"- verified subtitles: {verified_subtitles}",
        f"- unverified subtitles: {unverified_subtitles}",
        f"- row filter: {row_filter.value}",
    ]
    range_summary = _format_subtitle_range(first_index, last_index)
    if range_summary is not None:
        lines.append(range_summary)
    lines.extend(
        (
            f"- table rows: {len(rows)}",
            "",
            "## Audit Table",
            "",
            "| Subtitle | Guide | Target / revision | Notes |",
            "|---:|---|---|---|",
            *(row for _, _, row in rows),
        )
    )
    return "\n".join(lines) + "\n"


def _escape_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\\N", "\n").replace("\n", "<br>").replace("|", "\\|")


def _format_texts(texts: Sequence[str]) -> str:
    """Format zero or more subtitle texts for one table cell.

    Arguments:
        texts: subtitle texts to format
    Returns:
        subtitle texts separated by newlines, or an em dash if absent
    """
    if not texts:
        return "—"
    return "\n".join(texts)


def _format_subtitle_range(
    first_index: int | None,
    last_index: int | None,
) -> str | None:
    """Format an optional target subtitle range for the report summary.

    Arguments:
        first_index: first included 1-indexed target subtitle number
        last_index: last included 1-indexed target subtitle number
    Returns:
        formatted range summary, or None if the range is unbounded
    """
    if first_index is None and last_index is None:
        return None
    if first_index is None:
        return f"- target subtitle range: through {last_index}"
    if last_index is None:
        return f"- target subtitle range: from {first_index}"
    return f"- target subtitle range: {first_index} through {last_index}"


def _get_blocks_by_key(
    target: Series,
    guide: Series,
) -> dict[tuple[tuple[str, ...], tuple[str, ...]], list[_GuidedReviewBlock]]:
    """Index eligible target and guide blocks by their logged text.

    Arguments:
        target: target subtitle series provided for guided review
        guide: guide subtitle series provided for guided review
    Returns:
        guided-review blocks keyed by target and guide text
    """
    blocks_by_key: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[_GuidedReviewBlock],
    ] = defaultdict(list)
    target_offset = 0
    for block_number, (target_block, guide_block) in enumerate(
        get_block_pairs_by_pause(target, guide),
        1,
    ):
        target_indexes = tuple(
            range(target_offset + 1, target_offset + len(target_block) + 1)
        )
        target_offset += len(target_block)
        if not target_block or not guide_block:
            continue

        target_texts = tuple(
            subtitle.text_with_newline.strip() for subtitle in target_block
        )
        guide_texts = tuple(
            subtitle.text_with_newline.strip() for subtitle in guide_block
        )
        aligned_guide_texts: list[tuple[str, ...]] = [()] * len(target_block)
        for target_group, guide_group in get_sync_groups(target_block, guide_block):
            group_guide_texts = tuple(guide_texts[index] for index in guide_group)
            for target_index in target_group:
                aligned_guide_texts[target_index] = group_guide_texts
        blocks_by_key[(target_texts, guide_texts)].append(
            _GuidedReviewBlock(
                block_number=block_number,
                target_indexes=target_indexes,
                target_texts=target_texts,
                guide_texts=guide_texts,
                aligned_guide_texts=tuple(aligned_guide_texts),
            )
        )
    return blocks_by_key


def _get_test_case_block(
    test_case: GuidedReviewTestCase,
    blocks_by_key: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[_GuidedReviewBlock],
    ],
    *,
    test_case_index: int,
) -> _GuidedReviewBlock:
    """Match one logged test case to its unique subtitle block.

    Arguments:
        test_case: guided-review test case to match
        blocks_by_key: available blocks keyed by logged target and guide text
        test_case_index: one-based test case position used in error messages
    Returns:
        uniquely matched subtitle block
    Raises:
        ScinoephileError: if the test case has no unique matching block
    """
    key = (
        tuple(target.text for target in test_case.query.targets),
        tuple(guide.text for guide in test_case.query.guides),
    )
    matches = blocks_by_key.get(key, [])
    if not matches:
        raise ScinoephileError(
            "Unable to audit guided review: "
            f"test case {test_case_index} was not found in the target and guide "
            "subtitle blocks"
        )
    if len(matches) > 1:
        block_numbers = ", ".join(str(match.block_number) for match in matches)
        raise ScinoephileError(
            "Unable to audit guided review: "
            f"test case {test_case_index} is ambiguous; it matches blocks "
            f"{block_numbers}"
        )
    return matches[0]
