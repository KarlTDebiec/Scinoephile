#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed 中文 subtitles from PaddleOCR and Google Lens."""

from __future__ import annotations

import asyncio
from logging import info, warning
from pathlib import Path

from scinoephile.common.validation import val_output_path
from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_llm_queryer import (
    ZhongwenFusionLLMQueryer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_test_case import (
    ZhongwenFusionTestCase,
)
from scinoephile.testing import (
    get_test_cases_from_file_path,
    test_data_root,
    update_test_cases,
)


class ZhongwenFuser:
    """Fuses OCRed 中文 subtitles from PaddleOCR and Google Lens."""

    def __init__(
        self,
        test_cases: list[ZhongwenFusionTestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
    ):
        """Initialize.

        Arguments:
            test_cases: test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
        """
        if test_cases is None:
            test_cases = self.get_default_test_cases()

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            test_cases.extend(get_test_cases_from_file_path(test_case_path))
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        self.llm_queryer = ZhongwenFusionLLMQueryer(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """Queries LLM to fuse OCRed 中文 text from PaddleOCR and Google Lens."""

    def fuse(self, paddle: Series, lens: Series, stop_at_idx: int | None = None):
        """Fuse OCRed 中文 text from PaddleOCR and Google Lens.

        Arguments:
            paddle: 中文 subtitles OCRed using PaddleOCR
            lens: 中文 subtitles OCRed using Google Lens
            stop_at_idx: stop processing at this index
        """
        # Validate series
        if not are_series_one_to_one(paddle, lens):
            raise ScinoephileError(
                "PaddleOCR and Google Lens series must have the same number of "
                "subtitles."
            )

        # Ensure test case file exists
        if self.test_case_path is not None and not self.test_case_path.exists():
            self.test_case_path.parent.mkdir(parents=True, exist_ok=True)
            self.create_test_case_file(self.test_case_path)

        # Fuse subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(paddle)
        for sub_idx, (paddle_sub, lens_sub) in enumerate(zip(paddle, lens)):
            if sub_idx >= stop_at_idx:
                break
            paddle_text = paddle_sub.text
            lens_text = lens_sub.text
            if not paddle_text and not lens_text:
                output_subtitles.append(
                    Subtitle(start=paddle_sub.start, end=paddle_sub.end, text="")
                )
                info(f"Subtitle {sub_idx + 1} empty.")
                continue
            if paddle_text == lens_text:
                output_subtitles.append(paddle_sub)
                info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{paddle_text.replace('\n', ' ')}"
                )
                continue
            if not paddle_text:
                if not lens_text:
                    continue
                output_subtitles.append(lens_sub)
                info(
                    f"Subtitle {sub_idx + 1} from Lens:      "
                    f"{lens_text.replace('\n', ' ')}"
                )
                continue
            if not lens_text:
                output_subtitles.append(paddle_sub)
                info(
                    f"Subtitle {sub_idx + 1} from PaddleOCR: "
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
            info(
                f"Subtitle {sub_idx + 1} fused:         {sub.text.replace('\n', '\\n')}"
            )
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

    @classmethod
    def get_default_test_cases(cls):
        """Get default test cases included with package.

        Returns:
            test cases
        """
        try:
            # noinspection PyUnusedImports
            from test.data.kob import kob_zhongwen_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.mlamd import mlamd_zhongwen_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.mnt import mnt_zhongwen_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.t import t_zhongwen_fusion_test_cases

            return (
                kob_zhongwen_fusion_test_cases
                + mlamd_zhongwen_fusion_test_cases
                + mnt_zhongwen_fusion_test_cases
                + t_zhongwen_fusion_test_cases
            )
        except ImportError as exc:
            warning(
                f"Default test cases not available for {cls.__name__}, "
                f"encountered Exception:\n{exc}"
            )
            return []

    @staticmethod
    def create_test_case_file(test_case_path: Path):
        """Create a test case file.

        Arguments:
            test_case_path: path to file to create
        """
        contents = '''"""中文 fusion test cases."""

from __future__ import annotations

from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase

# noinspection PyArgumentList
test_cases = []  # test_cases
"""中文 fusion test cases."""

__all__ = [
    "test_cases",
]'''
        test_case_path.write_text(contents, encoding="utf-8")
        info(f"Created test case file at {test_case_path}.")
