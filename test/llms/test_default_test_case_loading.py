#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression tests for default test-case loading."""

from __future__ import annotations

import json
from collections.abc import Callable

import pytest

from scinoephile.common import package_root
from scinoephile.core.llms import TestCase
from scinoephile.lang.eng.block_review import EngBlockReviewPrompt
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.zho.block_review import (
    ZhoHansBlockReviewPrompt,
    ZhoHantBlockReviewPrompt,
)
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.llms.default_test_cases import (
    ENG_BLOCK_REVIEW_JSON_PATHS,
    ENG_OCR_FUSION_JSON_PATHS,
    YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
    YUE_ZHO_LINE_REVIEW_JSON_PATHS,
    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANS_OCR_FUSION_JSON_PATHS,
    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANT_OCR_FUSION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block.manager import DualBlockManager
from scinoephile.llms.dual_block_gapped.manager import DualBlockGappedManager
from scinoephile.llms.dual_single.ocr_fusion.manager import OcrFusionManager
from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.multilang.yue_zho.block_review import YueVsZhoYueHansBlockReviewPrompt
from scinoephile.multilang.yue_zho.line_review import YueVsZhoYueHansLineReviewPrompt
from scinoephile.multilang.yue_zho.line_review.manager import YueZhoLineReviewManager
from scinoephile.multilang.yue_zho.translation import YueVsZhoYueHansTranslationPrompt


def _get_expected_case_count(relative_paths: list[str]) -> int:
    """Get expected number of test cases from JSON files.

    Arguments:
        relative_paths: paths relative to repository test data root
    Returns:
        expected number of test cases
    """
    test_data_root = package_root.parent / "test/data"
    count = 0
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as file_handle:
            count += len(json.load(file_handle))
    return count


@pytest.mark.parametrize(
    ("name", "loader", "relative_paths"),
    [
        (
            "eng_block_review",
            lambda: load_default_test_cases(
                MonoBlockManager, EngBlockReviewPrompt, ENG_BLOCK_REVIEW_JSON_PATHS
            ),
            [
                "kob/output/eng_ocr/lang/eng/block_review.json",
                "kob/output/eng/lang/eng/block_review.json",
                "mlamd/output/eng_ocr/lang/eng/block_review.json",
                "mnt/output/eng_ocr/lang/eng/block_review.json",
                "t/output/eng_ocr/lang/eng/block_review.json",
            ],
        ),
        (
            "eng_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager, EngOcrFusionPrompt, ENG_OCR_FUSION_JSON_PATHS
            ),
            [
                "kob/output/eng_ocr/lang/eng/ocr_fusion.json",
                "mlamd/output/eng_ocr/lang/eng/ocr_fusion.json",
                "mnt/output/eng_ocr/lang/eng/ocr_fusion.json",
                "t/output/eng_ocr/lang/eng/ocr_fusion.json",
            ],
        ),
        (
            "zho_hans_block_review",
            lambda: load_default_test_cases(
                MonoBlockManager,
                ZhoHansBlockReviewPrompt,
                ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/zho-Hans_ocr/lang/zho/block_review.json",
                "mnt/output/zho-Hans_ocr/lang/zho/block_review.json",
                "t/output/zho-Hans_ocr/lang/zho/block_review.json",
            ],
        ),
        (
            "zho_hant_block_review",
            lambda: load_default_test_cases(
                MonoBlockManager,
                ZhoHantBlockReviewPrompt,
                ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "kob/output/zho-Hant_ocr/lang/zho/block_review.json",
                "mlamd/output/zho-Hant_ocr/lang/zho/block_review.json",
                "mnt/output/zho-Hant_ocr/lang/zho/block_review.json",
                "t/output/zho-Hant_ocr/lang/zho/block_review.json",
            ],
        ),
        (
            "zho_hans_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager,
                ZhoHansOcrFusionPrompt,
                ZHO_HANS_OCR_FUSION_JSON_PATHS,
            ),
            [
                "mlamd/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
                "mnt/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
                "t/output/zho-Hans_ocr/lang/zho/ocr_fusion.json",
            ],
        ),
        (
            "zho_hant_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager,
                ZhoHantOcrFusionPrompt,
                ZHO_HANT_OCR_FUSION_JSON_PATHS,
            ),
            [
                "kob/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "mlamd/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "mnt/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
                "t/output/zho-Hant_ocr/lang/zho/ocr_fusion.json",
            ],
        ),
        (
            "yue_zho_line_review",
            lambda: load_default_test_cases(
                YueZhoLineReviewManager,
                YueVsZhoYueHansLineReviewPrompt,
                YUE_ZHO_LINE_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/line_review/mps.json",
            ],
        ),
        (
            "yue_zho_block_review",
            lambda: load_default_test_cases(
                DualBlockManager,
                YueVsZhoYueHansBlockReviewPrompt,
                YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/block_review/mps.json",
            ],
        ),
        (
            "yue_from_zho_translation",
            lambda: load_default_test_cases(
                DualBlockGappedManager,
                YueVsZhoYueHansTranslationPrompt,
                YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
            ),
            [
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/translation/cuda.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/translation/cpu.json",
                "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/translation/mps.json",
            ],
        ),
    ],
)
def test_default_loader_coverage(
    name: str,
    loader: Callable[[], list[TestCase]],
    relative_paths: list[str],
):
    """Test that each default loader includes all configured repository cases.

    Arguments:
        name: short name of loader under test
        loader: callable that loads default test cases
        relative_paths: expected JSON paths for this loader
    """
    expected_count = _get_expected_case_count(relative_paths)
    loaded_count = len(loader())
    assert loaded_count == expected_count, (
        f"{name} loaded {loaded_count} cases, expected {expected_count}"
    )
