#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes review of multiple guide-aligned subtitle sources."""

from __future__ import annotations

from collections.abc import Mapping
from logging import getLogger
from typing import cast

from scinoephile.common.validation import val_index_range
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Processor
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.core.text import replace_control_characters

from .manager import MultiReviewManager
from .models import MultiReviewAnswer
from .prompt import MultiReviewPrompt

__all__ = ["MultiReviewProcessor"]


logger = getLogger(__name__)


class MultiReviewProcessor(Processor):
    """Review multiple equal-status subtitle sources using a complete guide."""

    prompt: MultiReviewPrompt
    """Text for LLM correspondence."""

    manager_cls = MultiReviewManager
    """Manager class used to construct test-case models."""

    def process(  # noqa: PLR0912
        self,
        sources: Mapping[str, Series],
        guide: Series,
        stop_at_idx: int | None = None,
        *,
        start_at_idx: int = 0,
    ) -> Series:
        """Review guide-aligned sources in guide-defined blocks.

        Arguments:
            sources: named equal-status subtitle sources
            guide: complete guide whose timing and count define the output
            stop_at_idx: exclusive zero-based block index at which to stop processing
            start_at_idx: inclusive zero-based block index at which to start processing
        Returns:
            reviewed subtitles using guide timing
        Raises:
            ScinoephileError: if there are too few sources or timing is not
              guide-aligned
        """
        if len(sources) < 2:
            raise ScinoephileError("Multi-review requires at least two sources.")
        if not guide:
            raise ScinoephileError("Multi-review requires a nonempty guide.")

        guide_by_timing = {
            (subtitle.start, subtitle.end): subtitle for subtitle in guide
        }
        if len(guide_by_timing) != len(guide):
            raise ScinoephileError(
                "Multi-review guide subtitles must have unique start and end times."
            )

        source_text_by_name_and_timing: dict[str, dict[tuple[int, int], str]] = {}
        for source_name, source in sources.items():
            source_text_by_timing: dict[tuple[int, int], str] = {}
            for subtitle in source:
                timing = (subtitle.start, subtitle.end)
                if timing not in guide_by_timing:
                    raise ScinoephileError(
                        f"Multi-review source {source_name!r} contains timing {timing} "
                        "that is absent from the guide."
                    )
                if timing in source_text_by_timing:
                    raise ScinoephileError(
                        f"Multi-review source {source_name!r} contains duplicate "
                        f"timing {timing}."
                    )
                source_text_by_timing[timing] = subtitle.text_with_newline.strip()
            source_text_by_name_and_timing[source_name] = source_text_by_timing

        guide_blocks = guide.blocks
        output_blocks: list[Series | None] = [None] * len(guide_blocks)
        block_range = val_index_range(len(guide_blocks), start_at_idx, stop_at_idx)
        for block_idx in block_range:
            guide_block = guide_blocks[block_idx]
            source_items: list[dict[str, object]] = []
            for (
                source_name,
                source_text_by_timing,
            ) in source_text_by_name_and_timing.items():
                subtitles: list[dict[str, int | str]] = []
                for subtitle_idx, guide_subtitle in enumerate(guide_block, 1):
                    timing = (guide_subtitle.start, guide_subtitle.end)
                    source_text = source_text_by_timing.get(timing)
                    if source_text is not None:
                        subtitles.append({"index": subtitle_idx, "text": source_text})
                source_items.append({"name": source_name, "subtitles": subtitles})

            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            query = query_cls.model_validate(
                {
                    "sources": source_items,
                    "guides": [
                        {
                            "index": subtitle_idx,
                            "text": guide_subtitle.text_with_newline.strip(),
                        }
                        for subtitle_idx, guide_subtitle in enumerate(guide_block, 1)
                    ],
                }
            )
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            answer = cast(MultiReviewAnswer, test_case.answer)
            output_text_by_index = {
                output.index: output.text for output in answer.outputs
            }
            output_block = Series()
            for subtitle_idx, guide_subtitle in enumerate(guide_block, 1):
                output_text = replace_control_characters(
                    output_text_by_index[subtitle_idx]
                )
                output_block.append(
                    Subtitle(
                        start=guide_subtitle.start,
                        end=guide_subtitle.end,
                        text=output_text,
                    )
                )
            logger.info(f"Block {block_idx}:\n{output_block.to_simple_string()}")
            output_blocks[block_idx] = output_block

        self.save_encountered_test_cases()

        processed_blocks = [block for block in output_blocks if block is not None]
        if processed_blocks:
            output = get_concatenated_series(processed_blocks)
        else:
            output = Series()
        logger.info(f"Concatenated Series:\n{output.to_simple_string()}")
        return output
