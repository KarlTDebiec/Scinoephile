#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes review LLM queries."""

from __future__ import annotations

from logging import getLogger
from typing import cast

from scinoephile.core.llms import Processor
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.text import replace_control_characters

from .manager import ReviewManager
from .models import ReviewAnswer
from .prompt import ReviewPrompt

__all__ = ["ReviewProcessor"]


logger = getLogger(__name__)


class ReviewProcessor(Processor):
    """Processes review LLM queries."""

    prompt: ReviewPrompt
    """Text for LLM correspondence."""

    manager_cls = ReviewManager
    """Manager class used to construct test case models."""

    def process(
        self,
        series: Series,
        stop_at_idx: int | None = None,
        *,
        start_at_idx: int = 0,
    ) -> Series:
        """Process review LLM queries.

        Arguments:
            series: subtitles
            stop_at_idx: exclusive block index at which to stop processing
            start_at_idx: inclusive block index at which to start processing
        Returns:
            processed subtitles
        """
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        if start_at_idx < 0:
            raise ValueError("start_at_idx must be greater than or equal to 0")
        if stop_at_idx is None:
            stop_at_idx = len(series.blocks)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")
        elif start_at_idx > stop_at_idx:
            raise ValueError("start_at_idx must be less than or equal to stop_at_idx")

        # Track indices for logging
        current_idx = 0
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break
            start_idx = current_idx
            end_idx = current_idx + len(block)
            current_idx = end_idx
            if block_idx < start_at_idx:
                continue

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

            answer = cast(ReviewAnswer, test_case.answer)
            revision_text_by_index = {
                revision.index: revision.text for revision in answer.revisions
            }
            output_series = Series()
            for sub_idx, subtitle in enumerate(block, 1):
                output_text = revision_text_by_index.get(sub_idx)
                output_subtitle = type(subtitle)(**subtitle.as_dict())
                if output_text:
                    output_subtitle.text = replace_control_characters(output_text)
                output_series.append(output_subtitle)

            logger.info(
                f"Block {block_idx} ({start_idx} - {end_idx}):\n"
                f"{block.to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        self.save_test_cases()

        output_series_blocks = [
            series for series in output_series_to_concatenate if series is not None
        ]
        if output_series_blocks:
            output_series = get_concatenated_series(output_series_blocks)
        else:
            output_series = Series()
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
