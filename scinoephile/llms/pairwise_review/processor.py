#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes pairwise review."""

from __future__ import annotations

from logging import getLogger

import numpy as np

from scinoephile.core.llms import Processor
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.synchronization import get_sync_overlap_matrix
from scinoephile.core.text import replace_control_characters

from .manager import PairwiseReviewManager
from .prompt import PairwiseReviewPrompt

__all__ = ["PairwiseReviewProcessor"]


logger = getLogger(__name__)


class PairwiseReviewProcessor(Processor):
    """Processes pairwise review."""

    prompt_cls: type[PairwiseReviewPrompt]
    """Text for LLM correspondence."""

    manager_cls = PairwiseReviewManager
    """Manager class used to construct test case models."""

    def process(  # noqa: PLR0912
        self,
        target: Series,
        reference: Series,
        stop_at_idx: int | None = None,
    ) -> Series:
        """Review target subtitles one at a time against aligned references.

        Target subtitles are grouped by the reference subtitle with which they have
        the greatest overlap. The first target in each group is reviewed, preserving
        the tolerant alignment behavior of the original pairwise-review workflow.

        Arguments:
            target: subtitles to review
            reference: subtitles providing corresponding reference text
            stop_at_idx: exclusive block index at which to stop processing
        Returns:
            pairwise-reviewed target subtitles
        """
        block_pairs = get_block_pairs_by_pause(target, reference)
        output_blocks: list[Series | None] = [None] * len(block_pairs)
        if stop_at_idx is None:
            stop_at_idx = len(block_pairs)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")

        test_case_cls = PairwiseReviewManager.get_test_case_cls(self.prompt_cls)
        query_cls = test_case_cls.query_cls
        for block_idx, (target_block, reference_block) in enumerate(block_pairs):
            if block_idx >= stop_at_idx:
                break

            output_block = Series()
            if not reference_block:
                for subtitle in target_block:
                    output_block.append(type(subtitle)(**subtitle.as_dict()))
                output_blocks[block_idx] = output_block
                continue

            overlap = get_sync_overlap_matrix(target_block, reference_block)
            target_groups = [list() for _ in reference_block]
            for target_idx in range(len(target_block)):
                reference_idx = int(np.argmax(overlap[target_idx, :]))
                target_groups[reference_idx].append(target_idx)

            for reference_idx, target_group in enumerate(target_groups):
                if not target_group:
                    continue
                target_subtitle = target_block.events[target_group[0]]
                reference_subtitle = reference_block.events[reference_idx]
                target_text = target_subtitle.text_with_newline.strip()
                reference_text = reference_subtitle.text_with_newline.strip()
                output_text = ""
                if target_text != reference_text:
                    query = query_cls(
                        **{
                            self.prompt_cls.target: target_text,
                            self.prompt_cls.reference: reference_text,
                        }
                    )
                    test_case = test_case_cls(query=query)
                    test_case = self.queryer(test_case)
                    output_text = getattr(test_case.answer, self.prompt_cls.output)

                if output_text == "�":
                    continue
                output_subtitle = type(target_subtitle)(**target_subtitle.as_dict())
                if output_text:
                    output_subtitle.text = replace_control_characters(output_text)
                output_block.append(output_subtitle)

            logger.info(f"Block {block_idx}:\n{output_block.to_simple_string()}")
            output_blocks[block_idx] = output_block

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        processed_blocks = [block for block in output_blocks if block is not None]
        if processed_blocks:
            output = get_concatenated_series(processed_blocks)
        else:
            output = Series()
        logger.info(f"Concatenated Series:\n{output.to_simple_string()}")
        return output
