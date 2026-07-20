#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fills gaps in target subtitles using guide subtitles."""

from __future__ import annotations

from logging import getLogger
from typing import cast

import numpy as np

from scinoephile.common.validation import val_index_range
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Processor
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.core.synchronization import get_sync_overlap_matrix

from .manager import GapTranslationManager
from .models import GapTranslationTestCase
from .prompt import GapTranslationPrompt

__all__ = ["GapTranslationProcessor"]


logger = getLogger(__name__)


class GapTranslationProcessor(Processor):
    """Fills gaps in target subtitles using guide subtitles."""

    prompt: GapTranslationPrompt
    """Text for LLM correspondence."""

    manager_cls = GapTranslationManager
    """Manager class used to construct test case models."""

    def process(  # noqa: PLR0912, PLR0915
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
        *,
        start_at_idx: int = 0,
    ) -> Series:
        """Fill gaps in target subtitles using guide subtitles.

        Arguments:
            source_one: target subtitles, which may contain gaps
            source_two: guide subtitles providing complete reference text
            stop_at_idx: exclusive zero-based block index at which to stop processing
            start_at_idx: inclusive zero-based block index at which to start processing
        Returns:
            target subtitles with gaps filled
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        block_range = val_index_range(len(block_pairs), start_at_idx, stop_at_idx)
        for block_idx in block_range:
            target_block, guide_block = block_pairs[block_idx]

            # Determine missing target positions
            size = len(guide_block)
            overlap = get_sync_overlap_matrix(target_block, guide_block)
            sync_groups = [([], [guide_idx]) for guide_idx in range(len(guide_block))]
            for target_idx in range(len(target_block)):
                guide_idx = np.argmax(overlap[target_idx, :])
                sync_groups[guide_idx][0].append(target_idx)
            gaps = tuple(idx for idx, group in enumerate(sync_groups) if not group[0])
            if not gaps:
                output_series_to_concatenate[block_idx] = target_block
                continue

            # Query LLM
            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            targets: list[dict[str, int | str]] = []
            guides: list[dict[str, int | str]] = []
            target_idx = 0
            for guide_idx in range(size):
                index = guide_idx + 1
                if guide_idx not in gaps:
                    targets.append(
                        {
                            "index": index,
                            "text": target_block.events[
                                target_idx
                            ].text_with_newline.strip(),
                        }
                    )
                    target_idx += 1
                guides.append(
                    {
                        "index": index,
                        "text": guide_block.events[guide_idx].text_with_newline.strip(),
                    }
                )
            query = query_cls.model_validate({"targets": targets, "guides": guides})
            test_case = test_case_cls(query=query)
            test_case = cast(GapTranslationTestCase, self.queryer(test_case))

            if test_case.answer is None:
                raise ScinoephileError("Gap translation returned no answer.")
            target_text_by_index = {
                target.index: target.text for target in test_case.query.targets
            }
            output_text_by_index = {
                output.index: output.text for output in test_case.answer.outputs
            }
            output_series = Series()
            for guide_idx in range(size):
                guide_subtitle = guide_block[guide_idx]
                index = guide_idx + 1
                output_text = target_text_by_index.get(index)
                if output_text is None:
                    output_text = output_text_by_index[index]
                output_series.append(
                    Subtitle(
                        start=guide_subtitle.start,
                        end=guide_subtitle.end,
                        text=output_text,
                    )
                )

            logger.info(f"Block {block_idx + 1}:\n{target_block.to_simple_string()}")
            output_series_to_concatenate[block_idx] = output_series

        complete_range = block_range.start == 0 and block_range.stop == len(block_pairs)
        self.save_test_cases(prune=self.prune_test_cases or complete_range)

        output_series_blocks = [
            series for series in output_series_to_concatenate if series is not None
        ]
        if output_series_blocks:
            output_series = get_concatenated_series(output_series_blocks)
        else:
            output_series = Series()
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
