#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for tracked LLM test-case JSON fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import mark

from scinoephile.core import Language
from scinoephile.core.llms import Manager
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager
from test.helpers import test_data_root

_TEST_CASE_FAMILIES: tuple[tuple[str, type[Manager]], ...] = (
    ("*/output/*/lang/*/ocr_fusion.json", OcrFusionManager),
    ("*/output/*/lang/*/review.json", ReviewManager),
    ("*/output/*/lang/*/simplify_review.json", ReviewManager),
    (
        "*/output/*/lang/yue_zho/gap_translation/*.json",
        GapTranslationManager,
    ),
    (
        "*/output/*/lang/yue_zho/guided_review/*.json",
        GuidedReviewManager,
    ),
    (
        "*/output/*/lang/yue_zho/transcription/delineation/*.json",
        DelineationManager,
    ),
    (
        "*/output/*/lang/yue_zho/transcription/punctuation/*.json",
        PunctuationManager,
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


def _localize_prompt_text(text: str) -> str:
    """Make prompt text and correspondence aliases distinct from the base prompt.

    Arguments:
        text: base prompt text
    Returns:
        localized test text
    """
    return f"localized_{text}"


@mark.parametrize(
    ("input_path", "manager_cls"),
    _TEST_CASE_FILES,
    ids=[
        input_path.relative_to(test_data_root).as_posix()
        for input_path, _ in _TEST_CASE_FILES
    ],
)
def test_tracked_test_case_json_round_trips_canonically(
    input_path: Path,
    manager_cls: type[Manager],
    tmp_path: Path,
):
    """Tracked JSON should round-trip canonically through localized models.

    Arguments:
        input_path: path to the tracked JSON fixture
        manager_cls: operation manager used to validate the fixture
        tmp_path: temporary output directory
    """
    raw_test_cases = json.loads(input_path.read_text(encoding="utf-8"))
    localized_prompt = manager_cls.base_prompt.transformed(
        Language.zho_hans,
        _localize_prompt_text,
    )
    localized_test_cases = load_test_cases_from_json(
        input_path,
        manager_cls,
        prompt=localized_prompt,
    )
    assert localized_test_cases

    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    base_test_cases = []
    for raw_test_case, localized_test_case in zip(
        raw_test_cases,
        localized_test_cases,
        strict=True,
    ):
        base_test_case = base_test_case_cls.model_validate(raw_test_case)
        base_test_cases.append(base_test_case)
        round_tripped_test_case = base_test_case_cls.model_validate(
            localized_test_case.model_dump(mode="json")
        )
        assert round_tripped_test_case == base_test_case

    output_path = tmp_path / input_path.name
    save_test_cases_to_json(
        output_path,
        localized_test_cases,
        manager_cls,
    )
    saved_data = json.loads(output_path.read_text(encoding="utf-8"))
    canonical_data = [
        test_case.model_dump(
            mode="json",
            by_alias=True,
            exclude_defaults=True,
        )
        for test_case in base_test_cases
    ]
    assert saved_data == canonical_data

    reloaded_test_cases = load_test_cases_from_json(
        output_path,
        manager_cls,
        prompt=manager_cls.base_prompt,
    )
    assert [test_case.model_dump(mode="json") for test_case in reloaded_test_cases] == [
        test_case.model_dump(mode="json") for test_case in base_test_cases
    ]


def test_tracked_test_case_json_inventory_is_complete():
    """Fixture contract should cover every tracked test case."""
    test_case_count = sum(
        len(json.loads(input_path.read_text(encoding="utf-8")))
        for input_path, _ in _TEST_CASE_FILES
    )

    assert len(_TEST_CASE_FILES) == 78
    assert test_case_count == 23_784
