#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes guided translation."""

from __future__ import annotations

from logging import getLogger
from typing import cast

from scinoephile.core.llms import Processor
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series

from .manager import GuidedTranslationManager
from .models import GuidedTranslationAnswer
from .prompt import GuidedTranslationPrompt

__all__ = ["GuidedTranslationProcessor"]


logger = getLogger(__name__)


class GuidedTranslationProcessor(Processor):
    """Processes guided translation blocks."""

    prompt: GuidedTranslationPrompt
    """Text for LLM correspondence."""

    manager_cls = GuidedTranslationManager
    """Manager class used to construct test case models."""

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Translate source blocks using guide blocks.

        Arguments:
            source_one: source subtitles that determine output timing and count
            source_two: guide subtitles providing target-language reference text
            stop_at_idx: stop processing at this block index
        Returns:
            translated subtitles using source-one timing
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        if stop_at_idx is None:
            stop_at_idx = len(block_pairs)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs):
            if blk_idx >= stop_at_idx:
                break
            if not one_blk:
                output_series_to_concatenate[blk_idx] = Series()
                continue

            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            query = query_cls.model_validate(
                {
                    "subtitles": [
                        {
                            "index": idx,
                            "text": subtitle.text_with_newline.strip(),
                        }
                        for idx, subtitle in enumerate(one_blk.events, 1)
                    ],
                    "guides": [
                        {
                            "index": idx,
                            "text": guide.text_with_newline.strip(),
                        }
                        for idx, guide in enumerate(two_blk.events, 1)
                    ],
                }
            )
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            answer = cast(GuidedTranslationAnswer, test_case.answer)
            output_text_by_index = {
                output.index: output.text for output in answer.outputs
            }
            output_series = Series()
            for sub_idx, sub in enumerate(one_blk.events, 1):
                output = output_text_by_index[sub_idx]
                output_series.append(
                    Subtitle(start=sub.start, end=sub.end, text=output)
                )

            logger.info(f"Block {blk_idx}:\n{output_series.to_simple_string()}")
            output_series_to_concatenate[blk_idx] = output_series

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
