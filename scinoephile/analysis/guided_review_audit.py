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
from scinoephile.core.text import remove_punc_and_whitespace
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
    """Current target subtitle texts in the block."""
    guide_texts: tuple[str, ...]
    """Guide subtitle texts in the block."""
    aligned_guide_texts: tuple[tuple[str, ...], ...]
    """Timing-aligned guide texts for each target subtitle."""


@dataclass(frozen=True, kw_only=True)
class _GuidedReviewRow:
    """One final per-subtitle guided-review audit row."""

    subtitle_index: int
    """One-based target subtitle index."""
    test_case_index: int
    """One-based position of the source test case in the JSON."""
    markdown: str
    """Formatted Markdown table row."""
    revised: bool
    """Whether the answer revised this subtitle."""
    verified: bool
    """Whether the source test case is verified."""


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
    rows_by_subtitle_index: dict[int, _GuidedReviewRow] = {}

    for test_case_index, test_case in enumerate(test_cases, 1):
        try:
            block = _get_test_case_block(
                test_case,
                blocks_by_key,
                test_case_index=test_case_index,
            )
        except ScinoephileError:
            if _is_test_case_outside_range(
                test_case,
                target,
                guide,
                first_index=first_index,
                last_index=last_index,
            ):
                continue
            raise
        answer = test_case.answer
        revisions_by_index = (
            {revision.index: revision for revision in answer.revisions}
            if answer is not None
            else {}
        )

        _validate_selected_targets(
            test_case,
            block,
            first_index=first_index,
            last_index=last_index,
            test_case_index=test_case_index,
        )

        for local_index, (subtitle_index, query_target, guide_texts) in enumerate(
            zip(
                block.target_indexes,
                test_case.query.targets,
                block.aligned_guide_texts,
                strict=False,
            ),
            1,
        ):
            if (first_index is not None and subtitle_index < first_index) or (
                last_index is not None and subtitle_index > last_index
            ):
                continue

            revision = revisions_by_index.get(local_index)

            target_revision = query_target.text
            if revision is not None:
                target_revision = f"{query_target.text}\n{revision.text}"

            cells = (
                str(subtitle_index),
                str(block.block_number),
                _format_texts(guide_texts),
                target_revision,
                "",
                "✓" if test_case.verified else "",
            )
            rows_by_subtitle_index[subtitle_index] = _GuidedReviewRow(
                subtitle_index=subtitle_index,
                test_case_index=test_case_index,
                markdown=f"| {' | '.join(_escape_cell(cell) for cell in cells)} |",
                revised=revision is not None,
                verified=test_case.verified,
            )

    all_rows = sorted(
        rows_by_subtitle_index.values(),
        key=lambda row: (row.subtitle_index, row.test_case_index),
    )
    revised_subtitles = sum(row.revised for row in all_rows)
    verified_subtitles = sum(row.verified for row in all_rows)
    rows = [
        row
        for row in all_rows
        if not (row_filter is GuidedReviewAuditFilter.changes and not row.revised)
        and not (row_filter is GuidedReviewAuditFilter.unverified and row.verified)
    ]
    subtitles = len(all_rows)
    unchanged_subtitles = subtitles - revised_subtitles
    unverified_subtitles = subtitles - verified_subtitles
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
            "| Index | Block | Guide | Target / revision | Notes | Verified |",
            "|---:|---:|---|---|---|:---:|",
            *(row.markdown for row in rows),
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
        key = (_normalize_texts(target_texts), guide_texts)
        blocks_by_key[key].append(
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
        _normalize_texts(tuple(target.text for target in test_case.query.targets)),
        tuple(guide.text for guide in test_case.query.guides),
    )
    matches = blocks_by_key.get(key, [])
    if not matches:
        matches = [
            block
            for keyed_blocks in blocks_by_key.values()
            for block in keyed_blocks
            if block.guide_texts == key[1]
        ]
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


def _validate_selected_targets(
    test_case: GuidedReviewTestCase,
    block: _GuidedReviewBlock,
    *,
    first_index: int | None,
    last_index: int | None,
    test_case_index: int,
):
    """Validate selected logged targets against the current target block.

    This permits an audit of an unaffected prefix after later upstream
    delineation changes while rejecting selected rows whose indexing changed.

    Arguments:
        test_case: guided-review test case to validate
        block: current target and guide block matched to the case
        first_index: first included target subtitle number
        last_index: last included target subtitle number
        test_case_index: one-based test case position used in errors
    Raises:
        ScinoephileError: if selected logged targets no longer match current indexes
    """
    query_targets = tuple(target.text for target in test_case.query.targets)
    selected_positions = [
        position
        for position, subtitle_index in enumerate(block.target_indexes)
        if (first_index is None or subtitle_index >= first_index)
        and (last_index is None or subtitle_index <= last_index)
    ]
    if not selected_positions:
        return

    for position in selected_positions:
        if position >= len(query_targets) or _normalize_texts(
            (query_targets[position],)
        ) != _normalize_texts((block.target_texts[position],)):
            subtitle_index = block.target_indexes[position]
            raise ScinoephileError(
                "Unable to audit guided review: "
                f"test case {test_case_index} target segmentation no longer "
                f"matches subtitle index {subtitle_index}"
            )

    includes_block_end = last_index is None or last_index >= block.target_indexes[-1]
    if len(query_targets) != len(block.target_texts) and includes_block_end:
        raise ScinoephileError(
            "Unable to audit guided review: "
            f"test case {test_case_index} target block length changed from "
            f"{len(query_targets)} to {len(block.target_texts)} subtitles"
        )


def _normalize_texts(texts: tuple[str, ...]) -> tuple[str, ...]:
    """Normalize target texts for matching across punctuation-only changes.

    Arguments:
        texts: target subtitle texts
    Returns:
        texts without punctuation or whitespace
    """
    return tuple(remove_punc_and_whitespace(text) for text in texts)


def _is_test_case_outside_range(
    test_case: GuidedReviewTestCase,
    target: Series,
    guide: Series,
    *,
    first_index: int | None,
    last_index: int | None,
) -> bool:
    """Check whether an unmatched case is provably outside a bounded range.

    Later upstream changes can alter block grouping outside the requested audit
    range. Match the logged guide sequence directly by text and timing so those
    irrelevant cases do not prevent a partial audit.

    Arguments:
        test_case: unmatched guided-review test case
        target: current target subtitle series
        guide: current guide subtitle series
        first_index: first included target subtitle number
        last_index: last included target subtitle number
    Returns:
        whether every matching guide sequence lies outside the target time range
    """
    if first_index is None and last_index is None:
        return False

    selected_start = target[first_index - 1].start if first_index is not None else 0
    selected_end = (
        target[last_index - 1].end if last_index is not None else target[-1].end
    )
    query_guides = tuple(item.text for item in test_case.query.guides)
    guide_texts = tuple(subtitle.text_with_newline.strip() for subtitle in guide)
    starts = [
        index
        for index in range(len(guide_texts) - len(query_guides) + 1)
        if guide_texts[index : index + len(query_guides)] == query_guides
    ]
    if not starts:
        return False
    return all(
        guide[start + len(query_guides) - 1].end < selected_start
        or guide[start].start > selected_end
        for start in starts
    )
