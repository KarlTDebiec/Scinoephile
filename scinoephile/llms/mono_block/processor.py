#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes mono track / subtitle block matters."""

from __future__ import annotations

import re
from logging import info

from scinoephile.core.subtitles import Series, get_concatenated_series
from scinoephile.llms.base import Processor, save_test_cases_to_json

from .manager import MonoBlockManager
from .prompt import MonoBlockPrompt

__all__ = ["MonoBlockProcessor"]


class MonoBlockProcessor(Processor):
    """Processes mono track / subtitle block matters."""

    prompt_cls: type[MonoBlockPrompt]
    """Text for LLM correspondence."""

    manager_cls = MonoBlockManager
    """Manager class used to construct test case models."""

    def process(self, series: Series, stop_at_idx: int | None = None) -> Series:
        """Processes mono track / block matters.

        Arguments:
            series: subtitles
            stop_at_idx: stop processing at this index
        Returns:
            processed subtitles
        """
        # Process subtitles
        output_series_to_concatenate: list[Series | None] = [None] * len(series.blocks)
        stop_at_idx = stop_at_idx or len(series.blocks)
        for block_idx, block in enumerate(series.blocks):
            if block_idx >= stop_at_idx:
                break

            # Query LLM
            test_case_cls = MonoBlockManager.get_test_case_cls(
                len(block), self.prompt_cls
            )
            query_cls = test_case_cls.query_cls
            query_kwargs: dict[str, str] = {}
            for idx, subtitle in enumerate(block):
                key = self.prompt_cls.input(idx + 1)
                query_kwargs[key] = re.sub(r"\\N", "\n", subtitle.text).strip()
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_series = Series()
            for sub_idx, subtitle in enumerate(block):
                key = self.prompt_cls.output(sub_idx + 1)
                if output_text := getattr(test_case.answer, key):
                    subtitle.text = output_text
                output_series.append(subtitle)

            info(
                f"Block {block_idx} ({block.start_idx} - {block.end_idx}):\n"
                f"{block.to_series().to_simple_string()}"
            )
            output_series_to_concatenate[block_idx] = output_series

        # Log test cases
        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        # Organize and return
        output_series = get_concatenated_series(
            [s for s in output_series_to_concatenate if s is not None]
        )
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series
