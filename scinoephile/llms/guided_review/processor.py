#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes guided review."""

from __future__ import annotations

from logging import getLogger
from typing import cast

from scinoephile.common.validation import val_index_range
from scinoephile.core.llms import Processor
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.text import replace_control_characters

from .manager import GuidedReviewManager
from .models import GuidedReviewAnswer
from .prompt import GuidedReviewPrompt

__all__ = ["GuidedReviewProcessor"]


logger = getLogger(__name__)

_DELETION_MARKER = "�"


class GuidedReviewProcessor(Processor):
    """Processes guided review."""

    prompt: GuidedReviewPrompt
    """Text for LLM correspondence."""

    manager_cls = GuidedReviewManager
    """Manager class used to construct test case models."""

    def process(  # noqa: PLR0912
        self,
        target: Series,
        guide: Series,
        stop_at_idx: int | None = None,
        *,
        start_at_idx: int = 0,
    ) -> Series:
        """Review target blocks using guide blocks.

        Arguments:
            target: subtitles to review and whose timing is preserved
            guide: subtitles providing reference text
            stop_at_idx: exclusive zero-based block index at which to stop processing
            start_at_idx: inclusive zero-based block index at which to start processing
        Returns:
            guided-reviewed target subtitles
        """
        block_pairs = get_block_pairs_by_pause(target, guide)
        output_blocks: list[Series | None] = [None] * len(block_pairs)
        block_range = val_index_range(len(block_pairs), start_at_idx, stop_at_idx)

        for block_idx in block_range:
            target_block, guide_block = block_pairs[block_idx]
            if not target_block:
                output_blocks[block_idx] = Series()
                continue

            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            query = query_cls.model_validate(
                {
                    "targets": [
                        {
                            "index": idx,
                            "text": subtitle.text_with_newline.strip(),
                        }
                        for idx, subtitle in enumerate(target_block, 1)
                    ],
                    "guides": [
                        {
                            "index": idx,
                            "text": subtitle.text_with_newline.strip(),
                        }
                        for idx, subtitle in enumerate(guide_block, 1)
                    ],
                }
            )
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            answer = cast(GuidedReviewAnswer, test_case.answer)
            revision_text_by_index = {
                revision.index: revision.text for revision in answer.revisions
            }
            output_block = Series()
            for idx, subtitle in enumerate(target_block, 1):
                output_text = revision_text_by_index.get(idx)
                if output_text == _DELETION_MARKER:
                    continue
                output_subtitle = type(subtitle)(**subtitle.as_dict())
                if output_text:
                    output_subtitle.text = replace_control_characters(output_text)
                output_block.append(output_subtitle)
            logger.info(f"Block {block_idx}:\n{output_block.to_simple_string()}")
            output_blocks[block_idx] = output_block

        self.save_test_cases()

        processed_blocks = [block for block in output_blocks if block is not None]
        if processed_blocks:
            output = get_concatenated_series(processed_blocks)
        else:
            output = Series()
        logger.info(f"Concatenated Series:\n{output.to_simple_string()}")
        return output
