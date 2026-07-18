#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit gap-translation decisions and format them as Markdown."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_overlap_matrix
from scinoephile.llms.gap_translation import GapTranslationTestCase

from .audit_utils import (
    _escape_table_cell,
    _format_index_range,
    _validate_index_range,
)

__all__ = [
    "GapTranslationAuditFilter",
    "audit_gap_translation",
]


_GapTranslationKey = tuple[tuple[tuple[int, str], ...], tuple[str, ...]]


@dataclass(frozen=True, kw_only=True)
class _GapTranslationBlock:
    """One target and guide block available for gap translation."""

    block_number: int
    """One-based position in the complete block alignment."""
    guide_indexes: tuple[int, ...]
    """One-based global guide subtitle indexes in the block."""
    guide_texts: tuple[str, ...]
    """Guide subtitle texts in query-local order."""
    target_texts: tuple[str | None, ...]
    """Existing target text by guide position, with gaps represented by None."""


@dataclass(frozen=True, kw_only=True)
class _GapTranslationRow:
    """One translated gap displayed in the audit report."""

    answered: bool
    """Whether the source test case has an answer."""
    difficulty: int
    """Difficulty level of the source test case."""
    empty: bool
    """Whether the answer deliberately emitted empty text."""
    global_index: int
    """One-based global guide subtitle index."""
    markdown: str
    """Formatted Markdown table row."""
    test_case_index: int
    """One-based position of the source test case in the JSON."""
    verified: bool
    """Whether the source test case is verified."""


class GapTranslationAuditFilter(StrEnum):
    """Row filters supported by a gap-translation audit."""

    all = "all"
    """Include every translated or unanswered target gap."""

    unverified = "unverified"
    """Include only gaps from cases not marked as verified."""


def audit_gap_translation(
    target: Series,
    guide: Series,
    test_cases: Sequence[GapTranslationTestCase],
    *,
    difficulties: Sequence[int] = (),
    row_filter: GapTranslationAuditFilter = GapTranslationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit translations generated for gaps in a target subtitle series.

    Arguments:
        target: gapped target subtitle series provided for gap translation
        guide: complete guide subtitle series provided for gap translation
        test_cases: logged gap-translation test cases
        difficulties: exact case difficulty levels to include, or all if empty
        row_filter: row verification filter
        first_index: first 1-indexed guide subtitle number to include
        last_index: last 1-indexed guide subtitle number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a logged case cannot be matched uniquely to source data
    """
    _validate_index_range(first_index, last_index)
    if any(difficulty < 0 for difficulty in difficulties):
        raise ScinoephileError("Difficulty must be at least 0")
    difficulty_filter = tuple(sorted(set(difficulties)))

    blocks = _get_blocks(target, guide)
    active_cases = _get_active_test_case_blocks(
        guide,
        test_cases,
        blocks,
        difficulties=difficulty_filter,
        first_index=first_index,
        last_index=last_index,
    )
    all_rows: list[_GapTranslationRow] = []
    for test_case_index, test_case, block in active_cases:
        outputs_by_index = (
            {output.index: output.text for output in test_case.answer.outputs}
            if test_case.answer is not None
            else {}
        )
        for local_index, (global_index, guide_text, target_text) in enumerate(
            zip(
                block.guide_indexes,
                block.guide_texts,
                block.target_texts,
                strict=True,
            ),
            1,
        ):
            if target_text is not None:
                continue
            if (first_index is not None and global_index < first_index) or (
                last_index is not None and global_index > last_index
            ):
                continue

            answered = test_case.answer is not None
            output_text = outputs_by_index.get(local_index, "")
            empty = answered and not output_text
            if not answered:
                output_text = "(unanswered)"
            elif empty:
                output_text = "(empty)"
            cells = (
                f"G {global_index}\nQ {local_index}",
                f"C {test_case_index}\nB {block.block_number}",
                str(test_case.difficulty),
                guide_text,
                _format_target_context(block, local_index - 1),
                output_text,
                "",
                "✓" if test_case.verified else "",
            )
            all_rows.append(
                _GapTranslationRow(
                    answered=answered,
                    difficulty=test_case.difficulty,
                    empty=empty,
                    global_index=global_index,
                    markdown=(
                        f"| {' | '.join(_escape_table_cell(cell) for cell in cells)} |"
                    ),
                    test_case_index=test_case_index,
                    verified=test_case.verified,
                )
            )

    all_rows.sort(key=lambda row: (row.global_index, row.test_case_index))
    translated_gaps = sum(row.answered and not row.empty for row in all_rows)
    empty_translations = sum(row.empty for row in all_rows)
    unanswered_gaps = sum(not row.answered for row in all_rows)
    verified_gaps = sum(row.verified for row in all_rows)
    rows = [
        row
        for row in all_rows
        if not (row_filter is GapTranslationAuditFilter.unverified and row.verified)
    ]
    lines = [
        "# Gap Translation Audit",
        "",
        "## Summary",
        "",
        f"- logged cases: {len({row.test_case_index for row in all_rows})}",
        f"- gaps: {len(all_rows)}",
        f"- translated gaps: {translated_gaps}",
        f"- empty translations: {empty_translations}",
        f"- unanswered gaps: {unanswered_gaps}",
        f"- verified gaps: {verified_gaps}",
        f"- unverified gaps: {len(all_rows) - verified_gaps}",
        f"- row filter: {row_filter.value}",
    ]
    if difficulty_filter:
        difficulty_summary = ", ".join(str(value) for value in difficulty_filter)
        lines.append(f"- difficulty filter: {difficulty_summary}")
    else:
        lines.append("- difficulty filter: all")
    range_summary = _format_index_range(
        first_index,
        last_index,
        track_name="guide",
    )
    if range_summary is not None:
        lines.append(range_summary)
    lines.extend(
        (
            f"- table rows: {len(rows)}",
            "",
            "## Audit Table",
            "",
            (
                "| Indexes | Case / block | Difficulty | Guide | Target context | "
                "Translation | Notes | Verified |"
            ),
            "|---:|---:|---:|---|---|---|---|:---:|",
            *(row.markdown for row in rows),
        )
    )
    return "\n".join(lines) + "\n"


def _block_intersects_range(
    block: _GapTranslationBlock,
    first_index: int | None,
    last_index: int | None,
) -> bool:
    """Check whether a block has a target gap within an audit range.

    Arguments:
        block: gap-translation block to check
        first_index: first included guide subtitle number
        last_index: last included guide subtitle number
    Returns:
        whether any target gap in the block is selected
    """
    return any(
        target_text is None
        and (first_index is None or guide_index >= first_index)
        and (last_index is None or guide_index <= last_index)
        for guide_index, target_text in zip(
            block.guide_indexes,
            block.target_texts,
            strict=True,
        )
    )


def _format_target_context(block: _GapTranslationBlock, position: int) -> str:
    """Format the nearest existing target subtitles around one gap.

    Arguments:
        block: gap-translation block containing the gap
        position: zero-based guide position of the gap within the block
    Returns:
        nearest preceding and following target texts, or an em dash
    """
    context: list[str] = []
    for context_position in range(position - 1, -1, -1):
        text = block.target_texts[context_position]
        if text is not None:
            context.append(f"G {block.guide_indexes[context_position]}: {text}")
            break
    for context_position in range(position + 1, len(block.target_texts)):
        text = block.target_texts[context_position]
        if text is not None:
            context.append(f"G {block.guide_indexes[context_position]}: {text}")
            break
    if not context:
        return "—"
    return "\n".join(context)


def _get_active_test_case_blocks(
    guide: Series,
    test_cases: Sequence[GapTranslationTestCase],
    blocks: Sequence[_GapTranslationBlock],
    *,
    difficulties: Sequence[int],
    first_index: int | None,
    last_index: int | None,
) -> list[tuple[int, GapTranslationTestCase, _GapTranslationBlock]]:
    """Match current cases to blocks while ignoring superseded history.

    Arguments:
        guide: complete guide subtitle series
        test_cases: logged gap-translation test cases
        blocks: current target and guide blocks containing gaps
        difficulties: exact case difficulty levels to include, or all if empty
        first_index: first included guide subtitle number
        last_index: last included guide subtitle number
    Returns:
        current test cases paired with their unique blocks
    Raises:
        ScinoephileError: if a selected case is absent, stale, or ambiguous
    """
    blocks_by_key: dict[_GapTranslationKey, list[_GapTranslationBlock]] = defaultdict(
        list
    )
    blocks_by_guides: dict[tuple[str, ...], list[_GapTranslationBlock]] = defaultdict(
        list
    )
    for block in blocks:
        targets = tuple(
            (position, text)
            for position, text in enumerate(block.target_texts, 1)
            if text is not None
        )
        blocks_by_key[(targets, block.guide_texts)].append(block)
        blocks_by_guides[block.guide_texts].append(block)

    active_by_block_number: dict[
        int,
        tuple[int, GapTranslationTestCase, _GapTranslationBlock],
    ] = {}
    unmatched_cases: list[tuple[int, GapTranslationTestCase]] = []
    for test_case_index, test_case in enumerate(test_cases, 1):
        targets = tuple(
            (target.index, target.text) for target in test_case.query.targets
        )
        guides = tuple(guide_subtitle.text for guide_subtitle in test_case.query.guides)
        matches = blocks_by_key.get((targets, guides), [])
        selected_matches = [
            block
            for block in matches
            if _block_intersects_range(block, first_index, last_index)
        ]
        if not selected_matches:
            if matches or _is_test_case_outside_range(
                test_case,
                guide,
                first_index=first_index,
                last_index=last_index,
            ):
                continue
            unmatched_cases.append((test_case_index, test_case))
            continue
        if len(selected_matches) > 1:
            if difficulties and test_case.difficulty not in difficulties:
                continue
            block_numbers = ", ".join(
                str(block.block_number) for block in selected_matches
            )
            raise ScinoephileError(
                "Unable to audit gap translation: "
                f"test case {test_case_index} is ambiguous; it matches blocks "
                f"{block_numbers}"
            )
        block = selected_matches[0]
        active_by_block_number[block.block_number] = (
            test_case_index,
            test_case,
            block,
        )

    active_block_numbers = set(active_by_block_number)
    for test_case_index, test_case in unmatched_cases:
        if difficulties and test_case.difficulty not in difficulties:
            continue
        guides = tuple(guide_subtitle.text for guide_subtitle in test_case.query.guides)
        matches = blocks_by_guides.get(guides, [])
        selected_matches = [
            block
            for block in matches
            if _block_intersects_range(block, first_index, last_index)
        ]
        if not selected_matches:
            if matches:
                continue
            raise ScinoephileError(
                "Unable to audit gap translation: "
                f"test case {test_case_index} was not found in the target and guide "
                "subtitle blocks"
            )
        if all(
            block.block_number in active_block_numbers for block in selected_matches
        ):
            continue
        if len(selected_matches) > 1:
            block_numbers = ", ".join(
                str(block.block_number) for block in selected_matches
            )
            raise ScinoephileError(
                "Unable to audit gap translation: "
                f"test case {test_case_index} is ambiguous; its guide text matches "
                f"blocks {block_numbers}"
            )
        raise ScinoephileError(
            "Unable to audit gap translation: "
            f"test case {test_case_index} target subtitles no longer match block "
            f"{selected_matches[0].block_number}"
        )

    active_cases = [
        item
        for item in active_by_block_number.values()
        if not difficulties or item[1].difficulty in difficulties
    ]
    return sorted(active_cases, key=lambda item: item[2].block_number)


def _get_blocks(target: Series, guide: Series) -> list[_GapTranslationBlock]:
    """Reconstruct the target and guide blocks used for gap translation.

    Arguments:
        target: gapped target subtitle series
        guide: complete guide subtitle series
    Returns:
        blocks containing one or more missing target positions
    """
    blocks: list[_GapTranslationBlock] = []
    guide_offset = 0
    for block_number, (target_block, guide_block) in enumerate(
        get_block_pairs_by_pause(target, guide),
        1,
    ):
        guide_indexes = tuple(
            range(guide_offset + 1, guide_offset + len(guide_block) + 1)
        )
        guide_offset += len(guide_block)
        if not guide_block:
            continue

        overlap = get_sync_overlap_matrix(target_block, guide_block)
        occupied_positions = {int(row.argmax()) for row in overlap}
        if len(occupied_positions) == len(guide_block):
            continue

        target_texts: list[str | None] = [None] * len(guide_block)
        target_position = 0
        for guide_position in range(len(guide_block)):
            if guide_position not in occupied_positions:
                continue
            target_texts[guide_position] = target_block.events[
                target_position
            ].text_with_newline.strip()
            target_position += 1
        blocks.append(
            _GapTranslationBlock(
                block_number=block_number,
                guide_indexes=guide_indexes,
                guide_texts=tuple(
                    subtitle.text_with_newline.strip() for subtitle in guide_block
                ),
                target_texts=tuple(target_texts),
            )
        )
    return blocks


def _is_test_case_outside_range(
    test_case: GapTranslationTestCase,
    guide: Series,
    *,
    first_index: int | None,
    last_index: int | None,
) -> bool:
    """Check whether an unmatched case is provably outside a bounded range.

    Arguments:
        test_case: unmatched gap-translation test case
        guide: complete current guide subtitle series
        first_index: first included guide subtitle number
        last_index: last included guide subtitle number
    Returns:
        whether every matching guide span places all gaps outside the range
    """
    if first_index is None and last_index is None:
        return False

    query_guides = tuple(subtitle.text for subtitle in test_case.query.guides)
    guide_texts = tuple(subtitle.text_with_newline.strip() for subtitle in guide)
    gap_indexes = {subtitle.index for subtitle in test_case.query.guides} - {
        subtitle.index for subtitle in test_case.query.targets
    }
    matching_starts = [
        start
        for start in range(len(guide_texts) - len(query_guides) + 1)
        if guide_texts[start : start + len(query_guides)] == query_guides
    ]
    if not matching_starts:
        return False
    return all(
        all(
            (first_index is not None and start + gap_index < first_index)
            or (last_index is not None and start + gap_index > last_index)
            for gap_index in gap_indexes
        )
        for start in matching_starts
    )
