#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit standard and guided translation decisions as Markdown reports."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.llms.guided_translation import GuidedTranslationTestCase
from scinoephile.llms.translation import TranslationTestCase

from .utils import (
    VerificationAuditFilter,
    escape_table_cell,
    format_audit_report,
    validate_audit_range,
)

__all__ = [
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


def audit_guided_translation(
    source: Series,
    guide: Series,
    test_cases: Sequence[GuidedTranslationTestCase],
    *,
    row_filter: VerificationAuditFilter = VerificationAuditFilter.all,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
) -> str:
    """Audit guided translations against their source and guide blocks.

    Arguments:
        source: source-language subtitle series provided for translation
        guide: target-language guide subtitle series
        test_cases: logged guided-translation test cases
        row_filter: row verification filter
        first_index: first 1-indexed source subtitle number to include
        last_index: last 1-indexed source subtitle number to include
        first_block: first 1-indexed paired block number to include
        last_block: last 1-indexed paired block number to include
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if a range or logged case is invalid
    """
    # Build paired workflow blocks and validate the selection
    block_pairs = get_block_pairs_by_pause(source, guide)
    validate_audit_range(
        first_index,
        last_index,
        first_block,
        last_block,
        block_count=len(block_pairs),
    )
    blocks = _get_guided_blocks(block_pairs)

    # Audit the current blocks against the logged cases
    return _audit_translation_blocks(
        blocks,
        test_cases,
        title="Guided Translation Audit",
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def audit_translation(
    source: Series,
    test_cases: Sequence[TranslationTestCase],
    *,
    row_filter: VerificationAuditFilter = VerificationAuditFilter.all,
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

    # Audit the current blocks against the logged cases
    return _audit_translation_blocks(
        blocks,
        test_cases,
        title="Standard Translation Audit",
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def _audit_translation_blocks(
    blocks: Sequence[_TranslationBlock],
    test_cases: Sequence[_TranslationCase],
    *,
    title: str,
    row_filter: VerificationAuditFilter,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> str:
    """Audit matched standard or guided translation blocks.

    Arguments:
        blocks: current source blocks
        test_cases: logged translation cases
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
    cases_by_key: dict[_TranslationKey, tuple[int, _TranslationCase]] = {}
    for case_index, test_case in enumerate(test_cases, 1):
        cases_by_key[_get_case_key(test_case)] = (case_index, test_case)

    # Select current blocks and reject ambiguous repeated queries
    selected_block_data = _get_selected_block_data(
        blocks,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    # Match selected blocks to cases and format their rows
    all_rows: list[_TranslationRow] = []
    selected_case_indexes: set[int] = set()
    translated_subtitles = 0
    empty_translations = 0
    unanswered_subtitles = 0
    for block, selected_positions in selected_block_data:
        case_data = cases_by_key.get(block.key)
        if case_data is None:
            raise ScinoephileError(
                f"Unable to audit translation: block {block.block_number} has no "
                "matching logged test case"
            )
        case_index, test_case = case_data
        selected_case_indexes.add(case_index)

        outputs_by_index = {}
        if test_case.answer is not None:
            outputs_by_index = {
                output.index: output.text for output in test_case.answer.outputs
            }
        guide_text = _format_guide_text(block.guide_texts)
        verified_marker = ""
        if test_case.verified:
            verified_marker = "✓"
        for position in selected_positions:
            local_index = position + 1
            output_text = "(unanswered)"
            if test_case.answer is not None:
                output_text = outputs_by_index[local_index]
                if output_text:
                    translated_subtitles += 1
                else:
                    output_text = "(empty)"
                    empty_translations += 1
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
                verified_marker,
            )
            all_rows.append(
                _TranslationRow(
                    markdown=(
                        f"| {' | '.join(escape_table_cell(cell) for cell in cells)} |"
                    ),
                    verified=test_case.verified,
                )
            )

    # Apply the row filter after calculating complete selection statistics
    rows = [
        row
        for row in all_rows
        if not (row_filter is VerificationAuditFilter.unverified and row.verified)
    ]
    verified_subtitles = sum(row.verified for row in all_rows)
    return format_audit_report(
        title=title,
        summary_lines=(
            f"- logged cases: {len(selected_case_indexes)}",
            f"- subtitles: {len(all_rows)}",
            f"- translated subtitles: {translated_subtitles}",
            f"- empty translations: {empty_translations}",
            f"- unanswered subtitles: {unanswered_subtitles}",
            f"- verified subtitles: {verified_subtitles}",
            f"- unverified subtitles: {len(all_rows) - verified_subtitles}",
            f"- row filter: {row_filter.value}",
        ),
        column_labels=(
            "Indexes",
            "Case / block",
            "Difficulty",
            "Source",
            "Guide",
            "Translation",
            "Notes",
            "Verified",
        ),
        column_separators=("---:", "---:", "---:", "---", "---", "---", "---", ":---:"),
        rows=[row.markdown for row in rows],
        first_index=first_index,
        last_index=last_index,
        index_track_name="source",
        first_block=first_block,
        last_block=last_block,
    )


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


def _get_guided_blocks(
    block_pairs: Sequence[tuple[Series, Series]],
) -> list[_TranslationBlock]:
    """Build current guided-translation blocks with global source indexes.

    Arguments:
        block_pairs: paired source and guide workflow blocks
    Returns:
        current nonempty source blocks
    """
    blocks = []
    source_position = 0
    for block_number, (source_block, guide_block) in enumerate(block_pairs, 1):
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


def _get_selected_block_data(
    blocks: Sequence[_TranslationBlock],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> list[tuple[_TranslationBlock, list[int]]]:
    """Select block positions and reject indistinguishable repeated blocks.

    Arguments:
        blocks: current source blocks
        first_index: first included source subtitle number
        last_index: last included source subtitle number
        first_block: first included block number
        last_block: last included block number
    Returns:
        selected blocks and their zero-based source positions
    Raises:
        ScinoephileError: if selected blocks have identical logged query keys
    """
    # Select current blocks and source positions within the requested range
    selected_block_data: list[tuple[_TranslationBlock, list[int]]] = []
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

    # Reject repeated current blocks that cannot be matched uniquely to log cases
    selected_blocks_by_key: dict[_TranslationKey, list[_TranslationBlock]] = (
        defaultdict(list)
    )
    for block, _ in selected_block_data:
        selected_blocks_by_key[block.key].append(block)
    for matching_blocks in selected_blocks_by_key.values():
        if len(matching_blocks) < 2:
            continue
        block_numbers = ", ".join(str(block.block_number) for block in matching_blocks)
        raise ScinoephileError(
            "Unable to audit translation: "
            f"blocks {block_numbers} have identical source and guide text and cannot "
            "be matched uniquely to logged test cases"
        )
    return selected_block_data


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
