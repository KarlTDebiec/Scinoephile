#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes gap translation matters."""

from __future__ import annotations

from logging import getLogger
from typing import cast

import numpy as np

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
    """Processes gap translation matters."""

    prompt: GapTranslationPrompt
    """Text for LLM correspondence."""

    manager_cls = GapTranslationManager
    """Manager class used to construct test case models."""

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Fill gaps in the primary series using the secondary series as reference.

        Arguments:
            source_one: primary subtitles (may contain gaps)
            source_two: secondary subtitles providing reference
            stop_at_idx: exclusive block index at which to stop processing
        Returns:
            primary subtitles with gaps filled
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            # Determine missing target positions
            size = len(two_blk)
            overlap = get_sync_overlap_matrix(one_blk, two_blk)
            sync_grps = [([], [two_idx]) for two_idx in range(len(two_blk))]
            for one_idx in range(len(one_blk)):
                two_idx = np.argmax(overlap[one_idx, :])
                sync_grps[two_idx][0].append(one_idx)
            gaps = tuple(idx for idx, group in enumerate(sync_grps) if not group[0])
            if not gaps:
                output_series_to_concatenate[blk_idx] = one_blk
                continue

            # Query LLM
            test_case_cls = self.test_case_cls
            query_cls = test_case_cls.query_cls
            targets: list[dict[str, int | str]] = []
            guides: list[dict[str, int | str]] = []
            one_idx = 0
            for two_idx in range(size):
                index = two_idx + 1
                if two_idx not in gaps:
                    targets.append(
                        {
                            "index": index,
                            "text": one_blk.events[one_idx].text_with_newline.strip(),
                        }
                    )
                    one_idx += 1
                guides.append(
                    {
                        "index": index,
                        "text": two_blk.events[two_idx].text_with_newline.strip(),
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
            for two_idx in range(size):
                two_sub = two_blk[two_idx]
                start = two_sub.start
                end = two_sub.end
                index = two_idx + 1
                output = target_text_by_index.get(index)
                if output is None:
                    output = output_text_by_index[index]
                output_series.append(Subtitle(start=start, end=end, text=output))

            logger.info(f"Block {blk_idx}:\n{one_blk.to_simple_string()}")
            output_series_to_concatenate[blk_idx] = output_series

        self.save_test_cases()

        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
