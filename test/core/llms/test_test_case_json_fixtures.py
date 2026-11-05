#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for tracked LLM test-case JSON fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import JsonValue, TypeAdapter
from pytest import mark

from scinoephile.core import Language
from scinoephile.core.llms import Manager, TestCase
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.lang.transcription import YueTranscriptionManager
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
    ("*/output/*/lang/yue_zho/gap_translation/*.json", GapTranslationManager),
    ("*/output/*/lang/yue_zho/guided_review/*.json", GuidedReviewManager),
    ("*/output/*/lang/yue_zho/transcription/delineation/*.json", DelineationManager),
    ("*/output/*/lang/yue_zho/transcription/punctuation/*.json", PunctuationManager),
)


def _get_test_case_files() -> list[tuple[Path, type[Manager]]]:
    """Get tracked test-case files and the managers that validate them.

    Returns:
        test-case file and manager pairs
    Raises:
        ValueError: if a value is invalid
    """
    test_case_files: list[tuple[Path, type[Manager]]] = []
    for pattern, manager_cls in _TEST_CASE_FAMILIES:
        input_paths = sorted(test_data_root.glob(pattern))
        if not input_paths:
            raise ValueError(f"Test-case family has no fixtures: {pattern}")
        test_case_files.extend((input_path, manager_cls) for input_path in input_paths)
    test_case_files.extend(
        (input_path, YueTranscriptionManager)
        for input_path in sorted(
            test_data_root.glob("*/output/*_transcribe/json/transcription.json")
        )
    )
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
def test_tracked_test_case_json_is_valid_and_round_trips(
    input_path: Path, manager_cls: type[Manager], tmp_path: Path
):
    """Validate every fixture and round-trip representative localized cases.

    Arguments:
        input_path: path to the tracked JSON fixture
        manager_cls: operation manager used to validate the fixture
        tmp_path: temporary output directory
    """
    raw_test_cases = TypeAdapter(list[dict[str, JsonValue]]).validate_json(
        input_path.read_text(encoding="utf-8"), strict=True
    )
    assert raw_test_cases
    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)

    # Validate the entire corpus once, including expensive transcription consensus
    representatives: dict[bool, TestCase] = {}
    for raw_test_case in raw_test_cases:
        test_case = base_test_case_cls.model_validate(
            raw_test_case,
            by_alias=True,
            by_name=False,
            strict=True,
            extra="forbid",
            context={"alias_only": True},
        )
        representatives.setdefault(test_case.answer is not None, test_case)

    # Alias conversion needs answered and unanswered cases, not every movie line
    base_test_cases = list(representatives.values())
    canonical_data = [
        test_case.model_dump(mode="json", by_alias=True, exclude_defaults=True)
        for test_case in base_test_cases
    ]
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(json.dumps(canonical_data), encoding="utf-8")
    localized_prompt = manager_cls.base_prompt.transformed(
        Language.zho_hans, _localize_prompt_text
    )
    localized_test_cases = load_test_cases_from_json(
        sample_path, manager_cls, prompt=localized_prompt
    )
    assert localized_test_cases

    for base_test_case, localized_test_case in zip(
        base_test_cases, localized_test_cases, strict=True
    ):
        round_tripped_test_case = base_test_case_cls.model_validate(
            localized_test_case.model_dump(mode="json")
        )
        assert round_tripped_test_case == base_test_case

    output_path = tmp_path / input_path.name
    save_test_cases_to_json(output_path, localized_test_cases, manager_cls)
    saved_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_data == canonical_data

    reloaded_test_cases = load_test_cases_from_json(
        output_path, manager_cls, prompt=manager_cls.base_prompt
    )
    assert [test_case.model_dump(mode="json") for test_case in reloaded_test_cases] == [
        test_case.model_dump(mode="json") for test_case in base_test_cases
    ]
