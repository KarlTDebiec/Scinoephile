#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed 中文 text from PaddleOCR and Google Lens OCR."""

from __future__ import annotations

import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from logging import info
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.core.zhongwen import get_zhongwen_cleaned
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_llm_queryer import (
    ZhongwenFusionLLMQueryer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_test_case import (
    ZhongwenFusionTestCase,
)
from scinoephile.testing import test_data_root, update_test_cases


class ZhongwenFuser:
    """Fuses OCRed 中文 text from PaddleOCR and Google Lens OCR."""

    def __init__(
        self,
        test_cases: list[ZhongwenFusionTestCase] | None = None,
        test_case_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            test_cases: test cases
            test_case_path: path to file containing test cases
        """
        if test_cases is None:
            test_cases = []
            # try:
            #     from test.data.kob import kob_zhongwen_proof_test_cases
            #     from test.data.mlamd import mlamd_zhongwen_proof_test_cases
            #     from test.data.t import t_zhongwen_proof_test_cases
            #
            #     test_cases = (
            #         kob_zhongwen_proof_test_cases
            #         + mlamd_zhongwen_proof_test_cases
            #         + t_zhongwen_proof_test_cases
            #     )
            # except ImportError:
            #     pass

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)

            if test_case_path.exists():
                spec = spec_from_file_location("test_cases", test_case_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                for name in getattr(module, "__all__", []):
                    if name.endswith("test_cases"):
                        if value := getattr(module, name, None):
                            test_cases.extend(value)

        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = ZhongwenFusionLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
        )
        """Queries LLM to fuse OCRed 中文 text from PaddleOCR and Google Lens OCR."""

    def fuse(self, paddle: Series, lens: Series, stop_at_idx: int | None = None):
        """Process all blocks.

        Arguments:
            paddle: subtitles OCRed using PaddleOCR
            lens: subtitles OCRed using Google Lens
            stop_at_idx: stop processing at this index
        """
        # Check and clean series
        if not are_series_one_to_one(paddle, lens):
            raise ScinoephileError(
                "PaddleOCR and Google Lens OCR series must have the same number of "
                "subtitles."
            )
        paddle = get_zhongwen_cleaned(paddle, remove_empty=False)
        lens = get_zhongwen_cleaned(lens, remove_empty=False)

        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.test_case_path.parent.mkdir(parents=True, exist_ok=True)
            self.create_test_case_file(self.test_case_path, len(paddle.blocks))

        # Run all blocks
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(paddle)
        for sub_idx, (paddle_sub, lens_sub) in enumerate(zip(paddle, lens)):
            if sub_idx >= stop_at_idx:
                break
            paddle_text = paddle_sub.text
            lens_text = lens_sub.text
            if paddle_text == lens_text:
                output_subtitles.append(paddle_sub)
                info(
                    f"Subtitle {sub_idx} identical:     "
                    f"{paddle_text.replace('\n', ' ')}"
                )
                continue
            if not paddle_text:
                if not lens_text:
                    continue
                output_subtitles.append(lens_sub)
                info(
                    f"Subtitle {sub_idx} from Lens:      {lens_text.replace('\n', ' ')}"
                )
                continue
            if not lens_text:
                output_subtitles.append(paddle_sub)
                info(
                    f"Subtitle {sub_idx} from PaddleOCR: "
                    f"{paddle_text.replace('\n', ' ')}"
                )
                continue
            query = ZhongwenFusionQuery(paddle=paddle_sub.text, lens=lens_sub.text)
            answer = self.llm_queryer(query)
            sub = Subtitle(
                start=paddle_sub.start,
                end=paddle_sub.end,
                text=answer.ronghe,
            )
            info(f"Subtitle {sub_idx} fused:         {sub.text.replace('\n', '\\n')}")
            output_subtitles.append(sub)

        # Concatenate and return
        output_series = Series()
        output_series.events = output_subtitles
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")

        if self.test_case_path is not None:
            asyncio.run(
                update_test_cases(self.test_case_path, "test_cases", self.llm_queryer)
            )
        return output_series

    @staticmethod
    def create_test_case_file(test_case_path: Path):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
        """
        contents = '''"""中文 fusion test cases."""

from __future__ import annotations

from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase

test_cases = []  # test_cases
"""中文 fusion test cases."""

__all__ = [
    "test_cases",
]'''
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")
