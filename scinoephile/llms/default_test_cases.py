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
    "ENG_OCR_FUSION_JSON_PATHS",
    "ENG_PROOFREADING_JSON_PATHS",
    "YUE_FROM_ZHO_TRANSLATION_JSON_PATHS",
    "YUE_ZHO_PROOFREADING_JSON_PATHS",
    "YUE_ZHO_REVIEW_JSON_PATHS",
    "ZHO_HANS_OCR_FUSION_JSON_PATHS",
    "ZHO_HANS_PROOFREADING_JSON_PATHS",
    "ZHO_HANT_OCR_FUSION_JSON_PATHS",
    "ZHO_HANT_PROOFREADING_JSON_PATHS",
    "get_repo_test_data_root",
    "load_default_test_cases_from_repo_data",
]

logger = getLogger(__name__)

ENG_PROOFREADING_JSON_PATHS = (
    Path("kob/lang/eng/proofreading/eng_ocr.json"),
    Path("kob/lang/eng/proofreading/eng_srt.json"),
    Path("mlamd/lang/eng/proofreading.json"),
    Path("mnt/lang/eng/proofreading.json"),
    Path("t/lang/eng/proofreading.json"),
)

ENG_OCR_FUSION_JSON_PATHS = (
    Path("kob/lang/eng/ocr_fusion.json"),
    Path("mlamd/lang/eng/ocr_fusion.json"),
    Path("mnt/lang/eng/ocr_fusion.json"),
    Path("t/lang/eng/ocr_fusion.json"),
)

ZHO_HANS_PROOFREADING_JSON_PATHS = (
    Path("mlamd/lang/zho/proofreading/zho-Hans.json"),
    Path("mnt/lang/zho/proofreading/zho-Hans.json"),
    Path("t/lang/zho/proofreading/zho-Hans.json"),
)

ZHO_HANT_PROOFREADING_JSON_PATHS = (
    Path("kob/lang/zho/proofreading/zho-Hant.json"),
    Path("mlamd/lang/zho/proofreading/zho-Hant.json"),
    Path("mnt/lang/zho/proofreading/zho-Hant.json"),
    Path("t/lang/zho/proofreading/zho-Hant.json"),
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

YUE_ZHO_PROOFREADING_JSON_PATHS = (Path("mlamd/multilang/yue_zho/proofreading.json"),)

YUE_ZHO_REVIEW_JSON_PATHS = (Path("mlamd/multilang/yue_zho/review.json"),)

YUE_FROM_ZHO_TRANSLATION_JSON_PATHS = (
    Path("mlamd/multilang/yue_zho/translation.json"),
)


@cache
def get_repo_test_data_root() -> Path | None:
    """Get repository test data root if available.

    Returns:
        path to repository test data root if available
    """
    test_data_root = package_root.parent / "test" / "data"
    if not test_data_root.is_dir():
        logger.info(
            "Repository test data directory is not available at %s; "
            "default test cases were not loaded.",
            test_data_root,
        )
        return None
    return test_data_root


@cache
def load_default_test_cases_from_repo_data(
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
    Raises:
        FileNotFoundError: if a configured test case file is not found
    """
    test_data_root = get_repo_test_data_root()
    if test_data_root is None:
        return ()

    loaded_test_cases: list[TestCase] = []
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(
                f"Configured default test case file is missing: {path}"
            )
        loaded_test_cases.extend(
            load_test_cases_from_json(path, manager_cls, prompt_cls=prompt_cls)
        )
    return tuple(loaded_test_cases)
