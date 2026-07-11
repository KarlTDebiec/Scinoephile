#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utility helpers for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .manager import Manager
from .prompt import Prompt
from .test_case import TestCase
from .test_case_mapping import remap_test_case

__all__ = [
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]


def load_test_cases_from_json(
    input_path: Path,
    manager_cls: type[Manager],
    prompt: Prompt,
) -> list[TestCase]:
    """Load test cases from JSON file.

    Arguments:
        input_path: path to JSON file containing test cases
        manager_cls: manager class used to construct test case models
        prompt: text for LLM correspondence
    Returns:
        list of test cases
    """
    with open(input_path, encoding="utf-8") as f:
        raw_test_cases: list[dict] = json.load(f)

    test_cases: list[TestCase] = []
    for test_case_data in raw_test_cases:
        base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
        base_test_case = base_test_case_cls.model_validate(
            test_case_data,
            extra="forbid",
        )
        test_case_cls = manager_cls.get_test_case_cls(prompt)
        test_cases.append(remap_test_case(base_test_case, test_case_cls))

    return test_cases


def save_test_cases_to_json(
    output_path: Path,
    test_cases: Iterable[TestCase],
    manager_cls: type[Manager],
):
    """Save test cases to JSON file.

    Arguments:
        output_path: path to JSON file to which to save
        test_cases: test cases to save
        manager_cls: manager class used to construct test case models
    """
    data = []
    for test_case in test_cases:
        base_test_case_cls = manager_cls.get_test_case_cls(
            manager_cls.base_prompt,
        )
        base_test_case = remap_test_case(test_case, base_test_case_cls)
        data.append(base_test_case.model_dump(mode="json", exclude_defaults=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
