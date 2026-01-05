#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base related to interactions with LLMs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .answer import Answer
from .llm_provider import LLMProvider
from .manager import Manager
from .prompt import Prompt
from .query import Query
from .queryer import Queryer
from .test_case import TestCase

__all__ = [
    "Answer",
    "LLMProvider",
    "Manager",
    "Prompt",
    "Query",
    "Queryer",
    "TestCase",
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]


def load_test_cases_from_json[TTestCase: TestCase](
    input_path: Path,
    manager_cls: type[Manager],
    **kwargs: Any,
) -> list[TTestCase]:
    """Load test cases from JSON file.

    Arguments:
        input_path: path to JSON file containing test cases
        manager_cls: manager class used to construct test case models
        **kwargs: additional keyword arguments passed to manager_cls
    Returns:
        list of test cases
    """
    with open(input_path, encoding="utf-8") as f:
        raw_test_cases: list[dict] = json.load(f)

    test_cases: list[TTestCase] = []
    for test_case_data in raw_test_cases:
        test_case_cls: type[TTestCase] = manager_cls.get_test_case_cls_from_data(
            test_case_data, **kwargs
        )
        test_case: TTestCase = test_case_cls.model_validate(test_case_data)
        test_cases.append(test_case)

    return test_cases


def save_test_cases_to_json(output_path: Path, test_cases: list[TestCase]):
    """Save test cases to JSON file.

    Arguments:
        output_path: path to JSON file to which to save
        test_cases: test cases to save
    """
    data = [tc.model_dump(exclude_defaults=True) for tc in test_cases]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
