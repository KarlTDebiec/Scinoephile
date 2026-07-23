#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit standard translations and provide shared translation-audit semantics."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.llms.translation import TranslationTestCase

from .utils import (
    format_audit_report,
    format_verification_marker,
    validate_audit_range,
)

__all__ = [
    "TranslationAuditBlock",
    "TranslationAuditCase",
    "TranslationAuditFilter",
    "audit_translation",
    "audit_translation_blocks",
    "resolve_translation_audit_output",
]

type _TranslationAuditKey = tuple[tuple[str, ...], tuple[str, ...]]
"""Source and guide text identifying one translation workflow block."""


class TranslationAuditFilter(StrEnum):
    """Row filters supported by translation audits."""

    all = "all"
    """Include every eligible row."""

    unverified = "unverified"
    """Include only rows from cases not marked as verified."""


@dataclass(frozen=True, kw_only=True)
class TranslationAuditBlock:
    """One current source block available for translation."""

    block_number: int
    """One-based position in the source or paired block sequence."""
    guide_texts: tuple[str, ...]
    """Guide texts supplied to guided translation, if any."""
    source_indexes: tuple[int, ...]
    """One-based global source subtitle indexes."""
    source_texts: tuple[str, ...]
    """Source subtitle texts in query order."""

    @property
    def key(self) -> _TranslationAuditKey:
        """Get the key matching this block to a logged test case.

        Returns:
            source and guide text identifying the block
        """
        return self.source_texts, self.guide_texts


@dataclass(frozen=True, kw_only=True)
class TranslationAuditCase:
    """Semantic data from one standard or guided translation test case."""

    case_index: int
    """One-based position of the test case in the JSON."""
    difficulty: int
    """Logged test-case difficulty."""
    key: _TranslationAuditKey
    """Source and guide text identifying the translated block."""
    outputs_by_index: Mapping[int, str] | None
    """Translated output by query-local index, or None when unanswered."""
    verified: bool
    """Whether the complete test case is verified."""


@dataclass(frozen=True, kw_only=True)
class _TranslationAuditRow:
    """One translated subtitle displayed in an audit report."""

    cells: tuple[str, ...]
    """Semantic audit table cell values."""
    verified: bool
    """Whether the source test case is verified."""


def audit_translation(
    source: Series,
    test_cases: Sequence[TranslationTestCase],
    *,
    row_filter: TranslationAuditFilter = TranslationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit standard translations against their source blocks.

    Arguments:
        source: source-language subtitle series provided for translation
        test_cases: logged standard-translation test cases
        row_filter: row verification filter
        first_index: first 1-indexed source subtitle number to include
        last_index: last 1-indexed source subtitle number to include
        first_block: first 1-indexed source block number to include
        last_block: last 1-indexed source block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a range or logged case is invalid
    """
    # Build current workflow blocks and validate the selection
    blocks = _get_standard_blocks(source)
    validate_audit_range(
        first_index,
        last_index,
        first_block,
        last_block,
        block_count=len(blocks),
    )

    # Adapt concrete test cases to shared semantic data
    cases = _get_standard_cases(test_cases)
    return audit_translation_blocks(
        blocks,
        cases,
        title="Standard Translation Audit",
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def audit_translation_blocks(
    blocks: Sequence[TranslationAuditBlock],
    cases: Sequence[TranslationAuditCase],
    *,
    title: str,
    row_filter: TranslationAuditFilter,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> str:
    """Audit semantic standard or guided translation blocks.

    Arguments:
        blocks: current source blocks
        cases: semantic logged translation cases
        title: report title
        row_filter: row verification filter
        first_index: first included source subtitle number
        last_index: last included source subtitle number
        first_block: first included block number
        last_block: last included block number
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a selected block lacks a logged test case
    """
    # Retain the latest logged case for each query
    cases_by_key = {case.key: case for case in cases}

    # Select current blocks and reject ambiguous repeated queries
    selected_block_data = _get_selected_block_data(
        blocks,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    # Match selected blocks to cases and build their semantic rows
    all_rows: list[_TranslationAuditRow] = []
    selected_case_indexes: set[int] = set()
    translated_subtitles = 0
    empty_translations = 0
    unanswered_subtitles = 0
    for block, selected_positions in selected_block_data:
        case = cases_by_key.get(block.key)
        if case is None:
            raise ScinoephileError(
                f"Unable to audit translation: block {block.block_number} has no "
                "matching logged test case"
            )
        selected_case_indexes.add(case.case_index)

        guide_text = _format_guide_text(block.guide_texts)
        verified_marker = format_verification_marker(case.verified)
        for position in selected_positions:
            local_index = position + 1
            output_text, answered, empty = resolve_translation_audit_output(
                case.outputs_by_index,
                local_index,
            )
            if not answered:
                unanswered_subtitles += 1
            elif empty:
                empty_translations += 1
            else:
                translated_subtitles += 1
            cells = (
                f"S {block.source_indexes[position]}\nQ {local_index}",
                f"C {case.case_index}\nB {block.block_number}",
                str(case.difficulty),
                block.source_texts[position],
                guide_text,
                output_text,
                "",
                verified_marker,
            )
            all_rows.append(
                _TranslationAuditRow(
                    cells=cells,
                    verified=case.verified,
                )
            )

    # Apply the row filter after calculating complete selection statistics
    rows = [
        row
        for row in all_rows
        if not (row_filter is TranslationAuditFilter.unverified and row.verified)
    ]
    verified_subtitles = sum(row.verified for row in all_rows)
    return format_audit_report(
        title=title,
        summary_items=(
            f"logged cases: {len(selected_case_indexes)}",
            f"subtitles: {len(all_rows)}",
            f"translated subtitles: {translated_subtitles}",
            f"empty translations: {empty_translations}",
            f"unanswered subtitles: {unanswered_subtitles}",
            f"verified subtitles: {verified_subtitles}",
            f"unverified subtitles: {len(all_rows) - verified_subtitles}",
            f"row filter: {row_filter.value}",
        ),
        columns=(
            ("Indexes", "right"),
            ("Case / block", "right"),
            ("Difficulty", "right"),
            ("Source", "left"),
            ("Guide", "left"),
            ("Translation", "left"),
            ("Notes", "left"),
            ("Verified", "center"),
        ),
        rows=[row.cells for row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="source",
        first_block=first_block,
        last_block=last_block,
    )


def resolve_translation_audit_output(
    outputs_by_index: Mapping[int, str] | None,
    local_index: int,
) -> tuple[str, bool, bool]:
    """Resolve one logged translation output for audit display.

    Arguments:
        outputs_by_index: output text by query-local index, or None when unanswered
        local_index: query-local output index
    Returns:
        display text, whether answered, and whether the answer is empty
    """
    if outputs_by_index is None:
        return "(unanswered)", False, False
    output_text = outputs_by_index[local_index]
    if not output_text:
        return "(empty)", True, True
    return output_text, True, False


def _format_guide_text(guide_texts: Sequence[str]) -> str:
    """Format a guided-translation block for one table cell.

    Arguments:
        guide_texts: guide texts in query order
    Returns:
        indexed guide text, or an em dash when absent
    """
    if not guide_texts:
        return "—"
    return "\n".join(f"G {index}: {text}" for index, text in enumerate(guide_texts, 1))


def _get_selected_block_data(
    blocks: Sequence[TranslationAuditBlock],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> list[tuple[TranslationAuditBlock, list[int]]]:
    """Select block positions within the requested range.

    Arguments:
        blocks: current source blocks
        first_index: first included source subtitle number
        last_index: last included source subtitle number
        first_block: first included block number
        last_block: last included block number
    Returns:
        selected blocks and their zero-based source positions
    """
    # Select current blocks and source positions within the requested range
    selected_block_data: list[tuple[TranslationAuditBlock, list[int]]] = []
    for block in blocks:
        if first_block is not None and block.block_number < first_block:
            continue
        if last_block is not None and block.block_number > last_block:
            continue
        selected_positions = [
            position
            for position, source_index in enumerate(block.source_indexes)
            if (first_index is None or source_index >= first_index)
            and (last_index is None or source_index <= last_index)
        ]
        if selected_positions:
            selected_block_data.append((block, selected_positions))

    return selected_block_data


def _get_standard_blocks(source: Series) -> list[TranslationAuditBlock]:
    """Build current standard-translation blocks with global source indexes.

    Arguments:
        source: source-language subtitle series
    Returns:
        current source blocks
    """
    blocks = []
    source_position = 0
    for block_number, source_block in enumerate(source.blocks, 1):
        source_indexes = tuple(
            range(source_position + 1, source_position + len(source_block) + 1)
        )
        source_position += len(source_block)
        blocks.append(
            TranslationAuditBlock(
                block_number=block_number,
                guide_texts=(),
                source_indexes=source_indexes,
                source_texts=tuple(
                    subtitle.text_with_newline.strip() for subtitle in source_block
                ),
            )
        )
    return blocks


def _get_standard_cases(
    test_cases: Sequence[TranslationTestCase],
) -> list[TranslationAuditCase]:
    """Adapt standard translation test cases to shared semantic data.

    Arguments:
        test_cases: concrete standard translation test cases
    Returns:
        semantic translation cases
    """
    cases = []
    for case_index, test_case in enumerate(test_cases, 1):
        outputs_by_index = None
        if test_case.answer is not None:
            outputs_by_index = {
                output.index: output.text for output in test_case.answer.outputs
            }
        cases.append(
            TranslationAuditCase(
                case_index=case_index,
                difficulty=test_case.difficulty,
                key=(
                    tuple(subtitle.text for subtitle in test_case.query.subtitles),
                    (),
                ),
                outputs_by_index=outputs_by_index,
                verified=test_case.verified,
            )
        )
    return cases
