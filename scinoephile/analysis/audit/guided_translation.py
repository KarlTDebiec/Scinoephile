#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit guided translation decisions and format them as Markdown."""

from __future__ import annotations

from collections.abc import Sequence

from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series
from scinoephile.llms.guided_translation import GuidedTranslationTestCase

from .translation import (
    TranslationAuditBlock,
    TranslationAuditCase,
    TranslationAuditFilter,
    audit_translation_blocks,
)
from .utils import validate_audit_range

__all__ = ["audit_guided_translation"]


def audit_guided_translation(
    source: Series,
    guide: Series,
    test_cases: Sequence[GuidedTranslationTestCase],
    *,
    row_filter: TranslationAuditFilter = TranslationAuditFilter.all,
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
    blocks = _get_blocks(block_pairs)

    # Adapt concrete test cases and run the shared audit engine
    cases = _get_cases(test_cases)
    return audit_translation_blocks(
        blocks,
        cases,
        title="Guided Translation Audit",
        row_filter=row_filter,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def _get_blocks(
    block_pairs: Sequence[tuple[Series, Series]],
) -> list[TranslationAuditBlock]:
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
            TranslationAuditBlock(
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


def _get_cases(
    test_cases: Sequence[GuidedTranslationTestCase],
) -> list[TranslationAuditCase]:
    """Adapt guided translation test cases to shared semantic data.

    Arguments:
        test_cases: concrete guided translation test cases
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
                    tuple(guide.text for guide in test_case.query.guides),
                ),
                outputs_by_index=outputs_by_index,
                verified=test_case.verified,
            )
        )
    return cases
