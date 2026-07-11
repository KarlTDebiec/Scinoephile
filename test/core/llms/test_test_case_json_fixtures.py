#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for tracked LLM test-case JSON fixtures."""

from __future__ import annotations

from pathlib import Path

from pytest import mark

from scinoephile.core.llms import Manager
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.pairwise_review import PairwiseReviewManager
from scinoephile.llms.review import ReviewManager
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoPunctuationManager,
)
from test.helpers import test_data_root

_TEST_CASE_FAMILIES: tuple[tuple[str, type[Manager]], ...] = (
    ("*/output/*/lang/*/ocr_fusion.json", OcrFusionManager),
    ("*/output/*/lang/*/review.json", ReviewManager),
    ("*/output/*/lang/*/simplify_review.json", ReviewManager),
    (
        "*/output/*/multilang/yue_zho/gap_translation/*.json",
        GapTranslationManager,
    ),
    (
        "*/output/*/multilang/yue_zho/guided_review/*.json",
        GuidedReviewManager,
    ),
    (
        "*/output/*/multilang/yue_zho/pairwise_review/*.json",
        PairwiseReviewManager,
    ),
    (
        "*/output/*/multilang/yue_zho/transcription/delineation/*.json",
        DelineationManager,
    ),
    (
        "*/output/*/multilang/yue_zho/transcription/punctuation/*.json",
        YueZhoPunctuationManager,
    ),
)


def _get_test_case_files() -> list[tuple[Path, type[Manager]]]:
    """Get tracked test-case files and the managers that validate them.

    Returns:
        test-case file and manager pairs
    """
    test_case_files: list[tuple[Path, type[Manager]]] = []
    for pattern, manager_cls in _TEST_CASE_FAMILIES:
        input_paths = sorted(test_data_root.glob(pattern))
        if not input_paths:
            raise ValueError(f"Test-case family has no fixtures: {pattern}")
        test_case_files.extend((input_path, manager_cls) for input_path in input_paths)
    return test_case_files


_TEST_CASE_FILES = _get_test_case_files()


@mark.parametrize(
    ("input_path", "manager_cls"),
    _TEST_CASE_FILES,
    ids=[
        input_path.relative_to(test_data_root).as_posix()
        for input_path, _ in _TEST_CASE_FILES
    ],
)
def test_tracked_test_case_json_is_valid(
    input_path: Path,
    manager_cls: type[Manager],
):
    """Tracked test-case JSON should load through its operation manager.

    Arguments:
        input_path: path to the tracked JSON fixture
        manager_cls: operation manager used to validate the fixture
    """
    test_cases = load_test_cases_from_json(
        input_path,
        manager_cls,
        prompt=manager_cls.base_prompt,
    )
    assert test_cases
