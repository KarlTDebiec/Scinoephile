#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression tests for default test-case loading."""

from __future__ import annotations

import json
from collections.abc import Callable

import pytest

from scinoephile.common import package_root
from scinoephile.core.llms import TestCase
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.lang.zho.block_review import (
    ZhoHansBlockReviewPrompt,
    ZhoHantBlockReviewPrompt,
)
from scinoephile.llms.default_test_cases import (
    ENG_OCR_FUSION_JSON_PATHS,
    ENG_PROOFREADING_JSON_PATHS,
    YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ZHO_PROOFREADING_JSON_PATHS,
    YUE_ZHO_REVIEW_JSON_PATHS,
    ZHO_HANS_OCR_FUSION_JSON_PATHS,
    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANT_OCR_FUSION_JSON_PATHS,
    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block.manager import DualBlockManager
from scinoephile.llms.dual_block_gapped.manager import DualBlockGappedManager
from scinoephile.llms.dual_single.ocr_fusion.manager import OcrFusionManager
from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.multilang.yue_zho.proofreading import YueZhoHansProofreadingPrompt
from scinoephile.multilang.yue_zho.proofreading.manager import YueZhoProofreadingManager
from scinoephile.multilang.yue_zho.review import YueHansReviewPrompt
from scinoephile.multilang.yue_zho.translation import YueHansFromZhoTranslationPrompt


def _get_expected_case_count(relative_paths: list[str]) -> int:
    """Get expected number of test cases from JSON files.

    Arguments:
        relative_paths: paths relative to repository test data root
    Returns:
        expected number of test cases
    """
    test_data_root = package_root.parent / "test" / "data"
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
            "eng_proofreading",
            lambda: load_default_test_cases(
                MonoBlockManager, EngProofreadingPrompt, ENG_PROOFREADING_JSON_PATHS
            ),
            [
                "kob/lang/eng/proofreading/eng_ocr.json",
                "kob/lang/eng/proofreading/eng_srt.json",
                "mlamd/lang/eng/proofreading.json",
                "mnt/lang/eng/proofreading.json",
                "t/lang/eng/proofreading.json",
            ],
        ),
        (
            "eng_ocr_fusion",
            lambda: load_default_test_cases(
                OcrFusionManager, EngOcrFusionPrompt, ENG_OCR_FUSION_JSON_PATHS
            ),
            [
                "kob/lang/eng/ocr_fusion.json",
                "mlamd/lang/eng/ocr_fusion.json",
                "mnt/lang/eng/ocr_fusion.json",
                "t/lang/eng/ocr_fusion.json",
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
                "mlamd/lang/zho/block_review/zho-Hans.json",
                "mnt/lang/zho/block_review/zho-Hans.json",
                "t/lang/zho/block_review/zho-Hans.json",
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
                "kob/lang/zho/block_review/zho-Hant.json",
                "mlamd/lang/zho/block_review/zho-Hant.json",
                "mnt/lang/zho/block_review/zho-Hant.json",
                "t/lang/zho/block_review/zho-Hant.json",
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
                "mlamd/lang/zho/ocr_fusion/zho-Hans.json",
                "mnt/lang/zho/ocr_fusion/zho-Hans.json",
                "t/lang/zho/ocr_fusion/zho-Hans.json",
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
                "kob/lang/zho/ocr_fusion/zho-Hant.json",
                "mlamd/lang/zho/ocr_fusion/zho-Hant.json",
                "mnt/lang/zho/ocr_fusion/zho-Hant.json",
                "t/lang/zho/ocr_fusion/zho-Hant.json",
            ],
        ),
        (
            "yue_zho_proofreading",
            lambda: load_default_test_cases(
                YueZhoProofreadingManager,
                YueZhoHansProofreadingPrompt,
                YUE_ZHO_PROOFREADING_JSON_PATHS,
            ),
            [
                "mlamd/multilang/yue_zho/proofreading/gpu.json",
                "mlamd/multilang/yue_zho/proofreading/cpu.json",
                "mlamd/multilang/yue_zho/proofreading/mps.json",
            ],
        ),
        (
            "yue_zho_review",
            lambda: load_default_test_cases(
                DualBlockManager,
                YueHansReviewPrompt,
                YUE_ZHO_REVIEW_JSON_PATHS,
            ),
            [
                "mlamd/multilang/yue_zho/review/gpu.json",
                "mlamd/multilang/yue_zho/review/cpu.json",
                "mlamd/multilang/yue_zho/review/mps.json",
            ],
        ),
        (
            "yue_from_zho_translation",
            lambda: load_default_test_cases(
                DualBlockGappedManager,
                YueHansFromZhoTranslationPrompt,
                YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
            ),
            [
                "mlamd/multilang/yue_zho/translation/gpu.json",
                "mlamd/multilang/yue_zho/translation/cpu.json",
                "mlamd/multilang/yue_zho/translation/mps.json",
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
