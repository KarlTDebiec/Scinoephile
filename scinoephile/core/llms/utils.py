#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utility helpers for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from scinoephile.common.file import open_atomic_text_file

from .manager import Manager
from .prompt import Prompt
from .test_case import TestCase

__all__ = ["load_test_cases_from_json", "save_test_cases_to_json"]

logger = getLogger(__name__)


def load_test_cases_from_json[TTestCase: TestCase](
    input_path: Path, manager_cls: type[Manager[TTestCase]], prompt: Prompt
) -> list[TTestCase]:
    """Load test cases from JSON file.

    Arguments:
        input_path: path to JSON file containing test cases
        manager_cls: manager class used to construct test case models
        prompt: text for LLM correspondence
    Returns:
        list of test cases
    """
    # Load input file as JSON and validate its basic shape
    with open(input_path, encoding="utf-8") as input_file:
        raw_test_cases: JsonValue = json.load(input_file)
    raw_test_case_items = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
        raw_test_cases, strict=True
    )

    # Validate each test case. Test cases are persisted using the field names in the
    # base prompt, so we need the test case class with that prompt to deserialize.
    base_test_case_cls = manager_cls.get_test_case_cls(prompt=manager_cls.base_prompt)
    base_test_cases = [
        base_test_case_cls.model_validate(
            raw_test_case,
            by_alias=True,
            by_name=False,
            strict=True,
            extra="forbid",
            context={"alias_only": True},
        )
        for raw_test_case in raw_test_case_items
    ]

    # Now that test cases have been deserialized, we revalidate them using the test case
    # class for our prompt.
    test_case_cls = manager_cls.get_test_case_cls(prompt=prompt)
    test_cases: list[TTestCase] = []
    for base_test_case in base_test_cases:
        test_case = test_case_cls.model_validate(base_test_case.model_dump(mode="json"))
        test_cases.append(test_case)

    return test_cases


def save_test_cases_to_json[TTestCase: TestCase](
    output_path: Path,
    test_cases: Iterable[TTestCase],
    manager_cls: type[Manager[TTestCase]],
):
    """Save test cases to JSON file.

    Arguments:
        output_path: path to JSON file to which to save
        test_cases: test cases to save
        manager_cls: manager class used to construct test case models
    """
    # Collect JSON for each test case, using the field names in the base prompt.
    base_test_case_cls = manager_cls.get_test_case_cls(prompt=manager_cls.base_prompt)
    test_case_jsons = []
    for test_case in test_cases:
        base_test_case = base_test_case_cls.model_validate(
            test_case.model_dump(mode="json"), strict=True
        )
        test_case_jsons.append(
            base_test_case.model_dump(mode="json", by_alias=True, exclude_defaults=True)
        )

    # Write output file
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)
        logger.info(f"Created directory {output_path.parent}")
    with open_atomic_text_file(output_path) as temp_file:
        json.dump(test_case_jsons, temp_file, ensure_ascii=False, indent=2)
    logger.info(f"Saved test cases to {output_path}")
