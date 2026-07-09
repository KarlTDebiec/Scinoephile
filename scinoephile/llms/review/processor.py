#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes review LLM queries."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core.llms import Processor
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.core.text import replace_control_characters

from .manager import ReviewManager
from .prompt import ReviewPrompt

__all__ = ["ReviewProcessor"]


logger = getLogger(__name__)


class ReviewProcessor(Processor):
    """Processes review LLM queries."""

    prompt_cls: type[ReviewPrompt]
    """Text for LLM correspondence."""

    manager_cls = ReviewManager
    """Manager class used to construct test case models."""

    def process(self, series: Series, stop_at_idx: int | None = None) -> Series:
        """Process review LLM queries.

        Arguments:
            series: subtitles
            stop_at_idx: exclusive block index at which to stop processing
        Returns:
            processed subtitles
        """
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        if stop_at_idx is None:
            stop_at_idx = len(series.blocks)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")

        # Track indices for logging
        current_idx = 0
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = ReviewManager.get_test_case_cls(
                len(block),
                self.prompt_cls,
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for idx, subtitle in enumerate(block.events):
                key = self.prompt_cls.input(idx + 1)
                query_kwargs[key] = subtitle.text_with_newline.strip()
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                key = self.prompt_cls.output(sub_idx + 1)
                output_text = getattr(test_case.answer, key)
                output_subtitle = type(subtitle)(**subtitle.as_dict())
                if output_text:
                    output_subtitle.text = replace_control_characters(output_text)
                output_series.append(output_subtitle)

            start_idx = current_idx
            end_idx = current_idx + len(block)
            current_idx = end_idx
            logger.info(
                f"Block {block_idx} ({start_idx} - {end_idx}):\n"
                f"{block.to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        output_series_blocks = [
            series for series in output_series_to_concatenate if series is not None
        ]
        if output_series_blocks:
            output_series = get_concatenated_series(output_series_blocks)
        else:
            output_series = Series()
        logger.info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
