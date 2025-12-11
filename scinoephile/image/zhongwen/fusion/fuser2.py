#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fuses OCRed Zhongwen subtitles from Google Lens and PaddleOCR."""

from __future__ import annotations

from logging import info, warning
from pathlib import Path

from scinoephile.core import ScinoephileError, Series, Subtitle
from scinoephile.core.llms import (
    Queryer2,
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.core.synchronization import are_series_one_to_one
from scinoephile.testing import test_data_root

from .prompt2 import ZhongwenFusionPrompt2
from .test_case2 import ZhongwenFusionTestCase2

__all__ = ["ZhongwenFuser2"]


class ZhongwenFuser2:
    """Fuses OCRed Zhongwen subtitles from Google Lens and PaddleOCR."""

    def __init__(
        self,
        test_cases: list[ZhongwenFusionTestCase2] | None = None,
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
            # noinspection PyTypeChecker
            test_cases.extend(
                load_test_cases_from_json(
                    test_case_path,
                    ZhongwenFusionTestCase2,
                    prompt_cls=ZhongwenFusionPrompt2,
                )
            )
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        queryer_cls = Queryer2.get_queryer_cls(ZhongwenFusionPrompt2)
        self.queryer = queryer_cls(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=test_data_root / "cache",
            auto_verify=auto_verify,
        )
        """LLM queryer."""

    def fuse(
        self, lens: Series, paddle: Series, stop_at_idx: int | None = None
    ) -> Series:
        """Fuse OCRed Zhongwen subtitles from Google Lens and PaddleOCR.

        Arguments:
            lens: Zhongwen subtitles OCRed using Google Lens
            paddle: Zhongwen subtitles OCRed using PaddleOCR
            stop_at_idx: stop processing at this index
        Returns:
            ronghe Zhongwen subtitles
        """
        # Validate series
        if not are_series_one_to_one(lens, paddle):
            raise ScinoephileError(
                "Google Lens and PaddleOCR series must have the same number of "
                "subtitles."
            )

        # Fuse subtitles
        output_subtitles = []
        stop_at_idx = stop_at_idx or len(lens)
        for sub_idx, (lens_sub, paddle_sub) in enumerate(zip(lens, paddle)):
            if sub_idx >= stop_at_idx:
                break
            lens_text = lens_sub.text
            paddle_text = paddle_sub.text

            # Handle missing data
            if not lens_text and not paddle_text:
                output_subtitles.append(
                    Subtitle(start=lens_sub.start, end=lens_sub.end, text="")
                )
                info(f"Subtitle {sub_idx + 1} empty.")
                continue
            if lens_text == paddle_text:
                output_subtitles.append(lens_sub)
                info(
                    f"Subtitle {sub_idx + 1} identical:     "
                    f"{lens_text.replace('\n', ' ')}"
                )
                continue
            if not paddle_text:
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

            # Query LLM
            test_case_cls = ZhongwenFusionTestCase2.get_test_case_cls()
            query_cls = test_case_cls.query_cls
            query = query_cls(lens=lens_sub.text, paddle=paddle_sub.text)
            test_case = test_case_cls(query=query)
            test_case = self.queryer(test_case)
            sub = Subtitle(
                start=lens_sub.start, end=lens_sub.end, text=test_case.answer.ronghe
            )
            info(
                f"Subtitle {sub_idx + 1} fused:         {sub.text.replace('\n', '\\n')}"
            )
            output_subtitles.append(sub)

        # Log test cases
        if self.test_case_path is not None:
            save_test_cases_to_json(
                self.test_case_path, self.queryer.encountered_test_cases.values()
            )

        # Organize and return
        output_series = Series()
        output_series.events = output_subtitles
        info(f"Concatenated Series:\n{output_series.to_simple_string()}")
        return output_series

    @classmethod
    def get_default_test_cases(cls):
        """Get default test cases included with package.

        Returns:
            test cases
        """
        try:
            # noinspection PyUnusedImports
            from test.data.kob import get_kob_zho_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.mlamd import get_mlamd_zho_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.mnt import get_mnt_zho_fusion_test_cases

            # noinspection PyUnusedImports
            from test.data.t import get_t_zho_fusion_test_cases

            return (
                get_kob_zho_fusion_test_cases()
                + get_mlamd_zho_fusion_test_cases()
                + get_mnt_zho_fusion_test_cases()
                + get_t_zho_fusion_test_cases()
            )
        except ImportError as exc:
            warning(
                f"Default test cases not available for {cls.__name__}, "
                f"encountered Exception:\n{exc}"
            )
        return []
