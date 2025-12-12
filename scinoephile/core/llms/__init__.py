#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code for working with LLMs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from .answer2 import Answer2
from .prompt2 import Prompt2
from .query2 import Query2
from .queryer2 import Queryer2
from .test_case2 import TestCase2

__all__ = [
    "Answer2",
    "Prompt2",
    "Query2",
    "Queryer2",
    "TestCase2",
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]


def load_test_cases_from_json[TTestCase: TestCase2](
    input_path: Path,
    test_case_base_cls: type[TTestCase],
    **kwargs: Any,
) -> list[TTestCase]:
    """Load test cases from JSON file.

    Arguments:
        input_path: path to JSON file containing test cases
        test_case_base_cls: test case class to use for test cases
        kwargs: additional keyword arguments passed to
          test_case_base_cls.get_test_case_cls
    Returns:
        list of test cases
    """
    with open(input_path, encoding="utf-8") as f:
        raw_test_cases: list[dict] = json.load(f)

    test_cases: list[TTestCase] = []
    for test_case_data in raw_test_cases:
        test_case_cls = test_case_base_cls.get_test_case_cls_from_data(
            test_case_data, **kwargs
        )
        test_cases.append(test_case_cls.model_validate(test_case_data))

    return test_cases


def save_test_cases_to_json(output_path: Path, test_cases: list[TestCase2]) -> None:
    """Save test cases to JSON file.

    Arguments:
        output_path: path to JSON file to which to save
        test_cases: test cases to save
    """
    data = [tc.model_dump(exclude_defaults=True) for tc in test_cases]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
