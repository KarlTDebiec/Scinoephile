#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code for working with LLMs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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
    "get_cls_name",
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]


def get_cls_name(base_name: str, suffix: str) -> str:
    """Build a Pydantic-valid class name from a base name and suffix.

    If the name exceeds the 64-character Pydantic limit, replace the suffix
    with a deterministic short hash.

    Arguments:
        base_name: name of base class
        suffix: descriptive suffix

    Returns:
        Valid class name string
    """
    # Base name and suffix are short enough to use directly
    if len(base_name) + 1 + len(suffix) <= 64:
        return f"{base_name}_{suffix}"

    # Base name is too long even for hash of suffix to be used
    if len(base_name) + 1 + 12 > 64:
        raise ValueError("Base name too long to create a valid Pydantic class name.")

    # Use base name and hash of suffix
    digest = hashlib.sha256(suffix.encode("utf-8")).hexdigest()[:12]
    return f"{base_name}_{digest}"


def load_test_cases_from_json(
    input_path: Path,
    test_case_base_cls: type[TestCase2],
    **kwargs: Any,
) -> list[TestCase2]:
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

    test_cases: list[TestCase2] = []
    for test_case_data in raw_test_cases:
        test_case_cls = test_case_base_cls.get_test_case_cls_from_data(
            test_case_data, **kwargs
        )
        test_cases.append(test_case_cls.model_validate(test_case_data))

    return test_cases


def save_test_cases_to_json(test_cases: list[TestCase2], output_path: Path) -> None:
    """Save test cases to JSON file.

    Arguments:
        test_cases: test cases to save
        output_path: path to JSON file to which to save
    """
    data = [tc.model_dump(exclude_defaults=True) for tc in test_cases]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
