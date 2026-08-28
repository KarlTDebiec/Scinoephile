#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utility helpers for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from pydantic import JsonValue, TypeAdapter

from scinoephile.common.file import open_atomic_text_file

from .manager import Manager
from .prompt import Prompt
from .test_case import TestCase

__all__ = ["load_test_cases_from_json", "save_test_cases_to_json"]


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
        cast(
            "TTestCase",
            base_test_case_cls.model_validate(
                raw_test_case,
                by_alias=True,
                by_name=False,
                strict=True,
                extra="forbid",
                context={"alias_only": True},
            ),
        )
        for raw_test_case in raw_test_case_items
    ]

    # Now that test cases have been deserialized, we revalidate them using the test case
    # class for our prompt.
    test_case_cls = manager_cls.get_test_case_cls(prompt=prompt)
    test_cases: list[TTestCase] = []
    for base_test_case in base_test_cases:
        test_case_data = base_test_case.model_dump(mode="json")
        test_case = test_case_cls.model_validate(test_case_data)
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
    # Revalidate every case through the canonical persistence schema
    test_cases_to_save = list(test_cases)
    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    data = []
    for test_case in test_cases_to_save:
        base_test_case = base_test_case_cls.model_validate(
            test_case.model_dump(mode="json"), strict=True
        )
        data.append(
            base_test_case.model_dump(mode="json", by_alias=True, exclude_defaults=True)
        )

    # Prepare the destination only after all cases pass validation
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Replace the destination atomically so failed writes preserve the prior file
    with open_atomic_text_file(output_path) as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
