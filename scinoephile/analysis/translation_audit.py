#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit standard and guided translation decisions as Markdown reports."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.llms.guided_translation import GuidedTranslationTestCase
from scinoephile.llms.translation import TranslationTestCase

from .audit_utils import (
    _escape_table_cell,
    _format_difficulty_filter,
    _format_index_range,
    _validate_index_range,
)

__all__ = [
    "TranslationAuditFilter",
    "audit_guided_translation",
    "audit_translation",
]

type _TranslationCase = TranslationTestCase | GuidedTranslationTestCase
type _TranslationKey = tuple[tuple[str, ...], tuple[str, ...]]


@dataclass(frozen=True, kw_only=True)
class _TranslationBlock:
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
    def key(self) -> _TranslationKey:
        """Key matching this block to a logged test case."""
        return self.source_texts, self.guide_texts


@dataclass(frozen=True, kw_only=True)
class _TranslationRow:
    """One translated subtitle displayed in an audit report."""

    markdown: str
    """Formatted Markdown table row."""
    verified: bool
    """Whether the source test case is verified."""


class TranslationAuditFilter(StrEnum):
    """Row filters supported by standard and guided translation audits."""

    all = "all"
    """Include every translated or unanswered source subtitle."""

    unverified = "unverified"
    """Include only subtitles from cases not marked as verified."""


def audit_guided_translation(
    source: Series,
    guide: Series,
    test_cases: Sequence[GuidedTranslationTestCase],
    *,
    difficulties: Sequence[int] = (),
    row_filter: TranslationAuditFilter = TranslationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit guided translations against their source and guide blocks.

    Arguments:
        source: source-language subtitle series provided for translation
        guide: target-language guide subtitle series
        test_cases: logged guided-translation test cases
        difficulties: exact case difficulty levels to include, or all if empty
        row_filter: row verification filter
        first_index: first 1-indexed source subtitle number to include
        last_index: last 1-indexed source subtitle number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a range, difficulty, or logged case is invalid
    """
    blocks = _get_guided_blocks(source, guide)
    return _audit_translation_blocks(
        blocks,
        test_cases,
        title="Guided Translation Audit",
        difficulties=difficulties,
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
    )


def audit_translation(
    source: Series,
    test_cases: Sequence[TranslationTestCase],
    *,
    difficulties: Sequence[int] = (),
    row_filter: TranslationAuditFilter = TranslationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
) -> str:
    """Audit standard translations against their source blocks.

    Arguments:
        source: source-language subtitle series provided for translation
        test_cases: logged standard-translation test cases
        difficulties: exact case difficulty levels to include, or all if empty
        row_filter: row verification filter
        first_index: first 1-indexed source subtitle number to include
        last_index: last 1-indexed source subtitle number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a range, difficulty, or logged case is invalid
    """
    blocks = _get_standard_blocks(source)
    return _audit_translation_blocks(
        blocks,
        test_cases,
        title="Standard Translation Audit",
        difficulties=difficulties,
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
    )


def _audit_translation_blocks(
    blocks: Sequence[_TranslationBlock],
    test_cases: Sequence[_TranslationCase],
    *,
    title: str,
    difficulties: Sequence[int],
    row_filter: TranslationAuditFilter,
    first_index: int | None,
    last_index: int | None,
) -> str:
    """Audit matched standard or guided translation blocks.

    Arguments:
        blocks: current source blocks
        test_cases: logged translation cases
        title: report title
        difficulties: exact case difficulty levels to include, or all if empty
        row_filter: row verification filter
        first_index: first included source subtitle number
        last_index: last included source subtitle number
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a selected block lacks a logged test case
    """
    _validate_index_range(first_index, last_index)
    if any(difficulty < 0 for difficulty in difficulties):
        raise ScinoephileError("Difficulty must be at least 0")
    difficulty_filter = tuple(sorted(set(difficulties)))

    cases_by_key: dict[_TranslationKey, tuple[int, _TranslationCase]] = {}
    for case_index, test_case in enumerate(test_cases, 1):
        cases_by_key[_get_case_key(test_case)] = (case_index, test_case)

    all_rows: list[_TranslationRow] = []
    selected_case_indexes: set[int] = set()
    answered_subtitles = 0
    unanswered_subtitles = 0
    for block in blocks:
        selected_positions = [
            position
            for position, source_index in enumerate(block.source_indexes)
            if (first_index is None or source_index >= first_index)
            and (last_index is None or source_index <= last_index)
        ]
        if not selected_positions:
            continue

        case_data = cases_by_key.get(block.key)
        if case_data is None:
            raise ScinoephileError(
                f"Unable to audit translation: block {block.block_number} has no "
                "matching logged test case"
            )
        case_index, test_case = case_data
        if difficulty_filter and test_case.difficulty not in difficulty_filter:
            continue
        selected_case_indexes.add(case_index)

        outputs_by_index = {}
        if test_case.answer is not None:
            outputs_by_index = {
                output.index: output.text for output in test_case.answer.outputs
            }
        guide_text = _format_guide_text(block.guide_texts)
        for position in selected_positions:
            local_index = position + 1
            output_text = "(unanswered)"
            if test_case.answer is not None:
                output_text = outputs_by_index[local_index]
                answered_subtitles += 1
            else:
                unanswered_subtitles += 1
            cells = (
                f"S {block.source_indexes[position]}\nQ {local_index}",
                f"C {case_index}\nB {block.block_number}",
                str(test_case.difficulty),
                block.source_texts[position],
                guide_text,
                output_text,
                "",
                "✓" if test_case.verified else "",
            )
            all_rows.append(
                _TranslationRow(
                    markdown=(
                        f"| {' | '.join(_escape_table_cell(cell) for cell in cells)} |"
                    ),
                    verified=test_case.verified,
                )
            )

    rows = [
        row
        for row in all_rows
        if not (row_filter is TranslationAuditFilter.unverified and row.verified)
    ]
    verified_subtitles = sum(row.verified for row in all_rows)
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        f"- logged cases: {len(selected_case_indexes)}",
        f"- subtitles: {len(all_rows)}",
        f"- translated subtitles: {answered_subtitles}",
        f"- unanswered subtitles: {unanswered_subtitles}",
        f"- verified subtitles: {verified_subtitles}",
        f"- unverified subtitles: {len(all_rows) - verified_subtitles}",
        f"- row filter: {row_filter.value}",
    ]
    lines.append(_format_difficulty_filter(difficulty_filter))
    range_summary = _format_index_range(
        first_index,
        last_index,
        track_name="source",
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
                "| Indexes | Case / block | Difficulty | Source | Guide | "
                "Translation | Notes | Verified |"
            ),
            "|---:|---:|---:|---|---|---|---|:---:|",
            *(row.markdown for row in rows),
        )
    )
    return "\n".join(lines) + "\n"


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


def _get_case_key(test_case: _TranslationCase) -> _TranslationKey:
    """Get the source and guide text key for a translation test case.

    Arguments:
        test_case: standard or guided translation test case
    Returns:
        source and guide text tuples
    """
    source_texts = tuple(subtitle.text for subtitle in test_case.query.subtitles)
    guide_texts: tuple[str, ...] = ()
    if isinstance(test_case, GuidedTranslationTestCase):
        guide_texts = tuple(guide.text for guide in test_case.query.guides)
    return source_texts, guide_texts


def _get_guided_blocks(source: Series, guide: Series) -> list[_TranslationBlock]:
    """Build current guided-translation blocks with global source indexes.

    Arguments:
        source: source-language subtitle series
        guide: target-language guide subtitle series
    Returns:
        current nonempty source blocks
    """
    blocks = []
    source_position = 0
    for block_number, (source_block, guide_block) in enumerate(
        get_block_pairs_by_pause(source, guide),
        1,
    ):
        if not source_block:
            continue
        source_indexes = tuple(
            range(source_position + 1, source_position + len(source_block) + 1)
        )
        source_position += len(source_block)
        blocks.append(
            _TranslationBlock(
                block_number=block_number,
                guide_texts=tuple(
                    subtitle.text_with_newline.strip() for subtitle in guide_block
                ),
                source_indexes=source_indexes,
                source_texts=tuple(
                    subtitle.text_with_newline.strip() for subtitle in source_block
                ),
            )
        )
    return blocks


def _get_standard_blocks(source: Series) -> list[_TranslationBlock]:
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
            _TranslationBlock(
                block_number=block_number,
                guide_texts=(),
                source_indexes=source_indexes,
                source_texts=tuple(
                    subtitle.text_with_newline.strip() for subtitle in source_block
                ),
            )
        )
    return blocks
