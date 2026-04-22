#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Helpers and path registries for default LLM test cases."""

from __future__ import annotations

from functools import cache
from logging import getLogger
from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core.llms import Manager, TestCase, load_test_cases_from_json

__all__ = [
    "ENG_BLOCK_REVIEW_JSON_PATHS",
    "ENG_OCR_FUSION_JSON_PATHS",
    "YUE_FROM_ZHO_TRANSLATION_JSON_PATHS",
    "YUE_ZHO_PROOFREADING_JSON_PATHS",
    "YUE_ZHO_REVIEW_JSON_PATHS",
    "YUE_ZHO_TRANSCRIPTION_PUNCTUATING_JSON_PATHS",
    "YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS",
    "ZHO_HANS_BLOCK_REVIEW_JSON_PATHS",
    "ZHO_HANS_OCR_FUSION_JSON_PATHS",
    "ZHO_HANT_BLOCK_REVIEW_JSON_PATHS",
    "ZHO_HANT_OCR_FUSION_JSON_PATHS",
    "load_default_test_cases",
]

logger = getLogger(__name__)

ENG_BLOCK_REVIEW_JSON_PATHS = (
    Path("kob/lang/eng/block_review/eng_ocr.json"),
    Path("kob/lang/eng/block_review/eng_srt.json"),
    Path("mlamd/lang/eng/block_review.json"),
    Path("mnt/lang/eng/block_review.json"),
    Path("t/lang/eng/block_review.json"),
)

ENG_OCR_FUSION_JSON_PATHS = (
    Path("kob/lang/eng/ocr_fusion.json"),
    Path("mlamd/lang/eng/ocr_fusion.json"),
    Path("mnt/lang/eng/ocr_fusion.json"),
    Path("t/lang/eng/ocr_fusion.json"),
)

ZHO_HANS_BLOCK_REVIEW_JSON_PATHS = (
    Path("mlamd/lang/zho/block_review/zho-Hans.json"),
    Path("mnt/lang/zho/block_review/zho-Hans.json"),
    Path("t/lang/zho/block_review/zho-Hans.json"),
)

ZHO_HANT_BLOCK_REVIEW_JSON_PATHS = (
    Path("kob/lang/zho/block_review/zho-Hant.json"),
    Path("mlamd/lang/zho/block_review/zho-Hant.json"),
    Path("mnt/lang/zho/block_review/zho-Hant.json"),
    Path("t/lang/zho/block_review/zho-Hant.json"),
)

ZHO_HANS_OCR_FUSION_JSON_PATHS = (
    Path("mlamd/lang/zho/ocr_fusion/zho-Hans.json"),
    Path("mnt/lang/zho/ocr_fusion/zho-Hans.json"),
    Path("t/lang/zho/ocr_fusion/zho-Hans.json"),
)

ZHO_HANT_OCR_FUSION_JSON_PATHS = (
    Path("kob/lang/zho/ocr_fusion/zho-Hant.json"),
    Path("mlamd/lang/zho/ocr_fusion/zho-Hant.json"),
    Path("mnt/lang/zho/ocr_fusion/zho-Hant.json"),
    Path("t/lang/zho/ocr_fusion/zho-Hant.json"),
)

YUE_ZHO_PROOFREADING_JSON_PATHS = (
    Path("mlamd/multilang/yue_zho/proofreading/gpu.json"),
    Path("mlamd/multilang/yue_zho/proofreading/cpu.json"),
    Path("mlamd/multilang/yue_zho/proofreading/mps.json"),
)

YUE_ZHO_REVIEW_JSON_PATHS = (
    Path("mlamd/multilang/yue_zho/review/gpu.json"),
    Path("mlamd/multilang/yue_zho/review/cpu.json"),
    Path("mlamd/multilang/yue_zho/review/mps.json"),
)

YUE_FROM_ZHO_TRANSLATION_JSON_PATHS = (
    Path("mlamd/multilang/yue_zho/translation/gpu.json"),
    Path("mlamd/multilang/yue_zho/translation/cpu.json"),
    Path("mlamd/multilang/yue_zho/translation/mps.json"),
)

YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS = (
    Path("kob/multilang/yue_zho/transcription/shifting/gpu.json"),
    Path("kob/multilang/yue_zho/transcription/shifting/mps.json"),
    Path("mlamd/multilang/yue_zho/transcription/shifting/gpu.json"),
    Path("mlamd/multilang/yue_zho/transcription/shifting/mps.json"),
)

YUE_ZHO_TRANSCRIPTION_PUNCTUATING_JSON_PATHS = (
    Path("kob/multilang/yue_zho/transcription/punctuating/gpu.json"),
    Path("kob/multilang/yue_zho/transcription/punctuating/mps.json"),
    Path("mlamd/multilang/yue_zho/transcription/punctuating/gpu.json"),
    Path("mlamd/multilang/yue_zho/transcription/punctuating/mps.json"),
)


@cache
def load_default_test_cases(
    manager_cls: type[Manager],
    prompt_cls: type,
    relative_paths: tuple[Path, ...],
) -> tuple[TestCase, ...]:
    """Load default test cases from repository JSON files and cache the result.

    Arguments:
        manager_cls: manager class used to construct test case models
        prompt_cls: text for LLM correspondence
        relative_paths: paths relative to repository test data root
    Returns:
        loaded test cases
    """
    test_data_root = package_root.parent / "test" / "data"
    if not test_data_root.is_dir():
        logger.info(f"Test data root {test_data_root} does not exist.")
        return tuple()

    loaded_test_cases: list[TestCase] = []
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            continue
        loaded_test_cases.extend(
            load_test_cases_from_json(path, manager_cls, prompt_cls=prompt_cls)
        )
        logger.info(f"Loaded {len(loaded_test_cases)} test cases from {path}.")
    return tuple(loaded_test_cases)
