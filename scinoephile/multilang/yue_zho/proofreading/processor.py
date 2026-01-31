#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes 粤文 vs. 中文 proofreading."""

from __future__ import annotations

from logging import getLogger

import numpy as np

from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, Subtitle, get_concatenated_series
from scinoephile.core.synchronization import get_sync_overlap_matrix
from scinoephile.llms.base import Processor, TestCase, save_test_cases_to_json

from .manager import YueZhoProofreadingManager
from .prompts import YueZhoHansProofreadingPrompt

logger = getLogger(__name__)
__all__ = ["YueZhoProofreadingProcessor"]


class YueZhoProofreadingProcessor(Processor):
    """Processes 粤文 vs. 中文 proofreading."""

    prompt_cls: type[YueZhoHansProofreadingPrompt]
    """Text for LLM correspondence."""

    manager_cls = YueZhoProofreadingManager
    """Manager class used to construct test case models."""

    def process(
        self,
        source_one: Series,
        source_two: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Proofread 粤文 against 中文 with tolerant alignment.

        Arguments:
            source_one: 粤文 subtitles (may omit some 中文 lines)
            source_two: 中文 reference subtitles
            stop_at_idx: stop processing at this block index
        Returns:
            Proofread 粤文 subtitles
        """
        block_pairs = get_block_pairs_by_pause(source_one, source_two)
        output_series_to_concatenate: list[Series | None] = [None] * len(block_pairs)
        stop_at_idx = stop_at_idx or len(block_pairs)
        for blk_idx, (one_blk, two_blk) in enumerate(block_pairs[:stop_at_idx]):
            if blk_idx >= stop_at_idx:
                break

            overlap = get_sync_overlap_matrix(one_blk, two_blk)
            output_block = Series()

            sync_grps = [([], [two_idx]) for two_idx in range(len(two_blk))]
            for one_idx in range(len(one_blk)):
                two_idx = np.argmax(overlap[one_idx, :])
                sync_grps[two_idx][0].append(one_idx)

            # Query LLM
            test_case_cls = YueZhoProofreadingManager.get_test_case_cls(
                prompt_cls=self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            for one_grp, two_grp in sync_grps:
                if not one_grp:
                    continue
                one_idx = one_grp[0]
                two_idx = two_grp[0]
                one_sub = one_blk.events[one_idx]
                two_sub = two_blk.events[two_idx]
                one_val = one_sub.text_with_newline.strip()
                two_val = two_sub.text_with_newline.strip()
                if one_val == two_val:
                    output_block.append(
                        Subtitle(start=one_sub.start, end=one_sub.end, text=one_val)
                    )
                    continue
                query_kwargs = {
                    self.prompt_cls.src_1: one_val,
                    self.prompt_cls.src_2: two_val,
                }
                query = query_cls(**query_kwargs)
                test_case = test_case_cls(query=query)
                test_case: TestCase = self.queryer(test_case)

                output = getattr(test_case.answer, self.prompt_cls.output)
                if output == "\ufffd":
                    continue
                output_block.append(
                    Subtitle(start=one_sub.start, end=one_sub.end, text=output)
                )

            logger.info(f"Block {blk_idx}:\n{one_blk.to_simple_string()}")
            output_series_to_concatenate[blk_idx] = output_block

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
