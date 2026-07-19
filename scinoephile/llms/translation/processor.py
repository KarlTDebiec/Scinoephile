#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes translation LLM queries."""

from __future__ import annotations

from logging import getLogger
from typing import cast

from scinoephile.common.validation import val_index_range
from scinoephile.core.llms import Processor
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.text import replace_control_characters

from .manager import TranslationManager
from .models import TranslationAnswer
from .prompt import TranslationPrompt

__all__ = ["TranslationProcessor"]


logger = getLogger(__name__)


class TranslationProcessor(Processor):
    """Processes translation LLM queries."""

    prompt: TranslationPrompt
    """Text for LLM correspondence."""

    manager_cls = TranslationManager
    """Manager class used to construct test case models."""

    def process(
        self,
        series: Series,
        stop_at_idx: int | None = None,
        *,
        start_at_idx: int = 0,
    ) -> Series:
        """Process translation LLM queries.

        Arguments:
            series: subtitles
            stop_at_idx: exclusive zero-based block index at which to stop processing
            start_at_idx: inclusive zero-based block index at which to start processing
        Returns:
            processed subtitles
        """
        # Process subtitles
        blocks = series.blocks
        output_series_to_concatenate: list[Series | None] = [None] * len(blocks)
        block_range = val_index_range(len(blocks), start_at_idx, stop_at_idx)

        # Track indices for logging
        current_idx = sum(len(block) for block in blocks[: block_range.start])
        for block_idx in block_range:
            block = blocks[block_idx]
            start_idx = current_idx
            end_idx = current_idx + len(block)
            current_idx = end_idx

            # Query LLM
            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            query = query_cls.model_validate(
                {
                    "subtitles": [
                        {
                            "index": idx,
                            "text": subtitle.text_with_newline.strip(),
                        }
                        for idx, subtitle in enumerate(block.events, 1)
                    ]
                }
            )
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            answer = cast(TranslationAnswer, test_case.answer)
            output_text_by_index = {
                output.index: output.text for output in answer.outputs
            }
            output_series = Series()
            for subtitle_idx, subtitle in enumerate(block, 1):
                output_text = output_text_by_index[subtitle_idx]
                output_subtitle = type(subtitle)(**subtitle.as_dict())
                output_subtitle.text = replace_control_characters(output_text)
                output_series.append(output_subtitle)

            logger.info(
                f"Block {block_idx + 1} "
                f"(subtitles {start_idx + 1} - {end_idx}):\n"
                f"{block.to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        self.save_test_cases()

        # Organize and return
        output_series_blocks = [
            series for series in output_series_to_concatenate if series is not None
        ]
        if output_series_blocks:
            output_series = get_concatenated_series(output_series_blocks)
        else:
            output_series = Series()
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
