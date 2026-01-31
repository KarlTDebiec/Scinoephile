#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes OCR fusion."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.llms.base import Processor, save_test_cases_to_json

from .manager import OcrFusionManager

logger = getLogger(__name__)
__all__ = ["OcrFusionProcessor"]


class OcrFusionProcessor(Processor):
    """Processes OCR fusion."""

    manager_cls = OcrFusionManager
    """Manager class used to construct test case models."""

    def process(
        self, source_one: Series, source_two: Series, stop_at_idx: int | None = None
    ) -> Series:
        """Processes OCR fusion dual track / single subtitle matters.

        Arguments:
            source_one: subtitles from source one
            source_two: subtitles from source two
            stop_at_idx: stop processing at this index
        Returns:
            processed subtitles
        """
        # Validate series
        if not are_series_one_to_one(source_one, source_two):
            raise ScinoephileError(
                "Series from sources one and two must have the same number of "
                f"subtitles; got {len(source_one)} and {len(source_two)}."
            )

        # Process subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(source_one)
        for sub_idx, (sub_one, sub_two) in enumerate(zip(source_one, source_two)):
            if sub_idx >= stop_at_idx:
                break
            text_one = sub_one.text
            text_two = sub_two.text

            # Handle missing data
            if not text_one and not text_two:
                output_subtitles.append(
                    Subtitle(start=sub_one.start, end=sub_one.end, text="")
                )
                logger.info(f"Subtitle {sub_idx + 1} empty.")
                continue
            if text_one == text_two:
                output_subtitles.append(sub_one)
                logger.info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{sub_one.text_with_newline.replace('\n', ' ')}"
                )
                continue
            if not text_two:
                output_subtitles.append(sub_one)
                logger.info(
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.src_1}: "
                    f"{sub_one.text_with_newline.replace('\n', ' ')}"
                )
                continue
            if not text_one:
                output_subtitles.append(sub_two)
                logger.info(
                    f"Subtitle {sub_idx + 1} from {self.prompt_cls.src_2}: "
                    f"{sub_two.text_with_newline.replace('\n', ' ')}"
                )
                continue

            # Query LLM
            test_case_cls = OcrFusionManager.get_test_case_cls(self.prompt_cls)
            query_cls = test_case_cls.query_cls
            query_kwargs = {
                self.prompt_cls.src_1: sub_one.text_with_newline,
                self.prompt_cls.src_2: sub_two.text_with_newline,
            }
            query = query_cls(**query_kwargs)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)

            output_text = getattr(test_case.answer, self.prompt_cls.output)
            sub = Subtitle(start=sub_one.start, end=sub_one.end, text=output_text)
            logger.info(
                f"Subtitle {sub_idx + 1} processed:     {sub.text.replace('\n', '\\n')}"
            )
            output_subtitles.append(sub)

        # Log test cases
        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        # Organize and return
        return Series(events=output_subtitles)
