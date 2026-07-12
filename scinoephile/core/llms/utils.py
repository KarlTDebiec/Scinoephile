#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utility helpers for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from pydantic import TypeAdapter

from scinoephile.common.file import open_atomic_text_file

from .manager import Manager
from .prompt import Prompt
from .test_case import TestCase

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
    # Prepare prompt-specific test-case classes
    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    test_case_cls = manager_cls.get_test_case_cls(prompt)

    # Load serialized test cases
    with open(input_path, encoding="utf-8") as input_file:
        raw_test_cases: object = json.load(input_file)

    # Validate using the base-prompt schema
    base_test_case_list_type = (
        list[base_test_case_cls]  # ty: ignore[invalid-type-form]
    )
    base_test_case_adapter = TypeAdapter(base_test_case_list_type)
    validated_base_test_cases = base_test_case_adapter.validate_python(
        raw_test_cases,
        by_alias=True,
        by_name=False,
        strict=True,
        extra="forbid",
        context={"alias_only": True},
    )
    base_test_cases = cast("list[TestCase]", validated_base_test_cases)

    # Convert to the requested prompt schema
    test_cases: list[TestCase] = []
    for base_test_case in base_test_cases:
        test_case_data = base_test_case.model_dump(mode="json")
        test_case = test_case_cls.model_validate(test_case_data)
        test_cases.append(test_case)

    return test_cases


def save_test_cases_to_json(
    output_path: Path,
    test_cases: Iterable[TestCase],
    manager_cls: type[Manager],
    *,
    prune: bool = False,
):
    """Save test cases to JSON file.

    Arguments:
        output_path: path to JSON file to which to save
        test_cases: test cases to save
        manager_cls: manager class used to construct test case models
        prune: whether to remove existing test cases that were not provided
    """
    test_cases_to_save = list(test_cases)
    if output_path.exists() and not prune:
        existing_test_cases = load_test_cases_from_json(
            output_path,
            manager_cls,
            manager_cls.base_prompt,
        )
        encountered_query_keys = {
            test_case.query.key for test_case in test_cases_to_save
        }
        test_cases_to_save = [
            test_case
            for test_case in existing_test_cases
            if test_case.query.key not in encountered_query_keys
        ] + test_cases_to_save

    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    data = []
    for test_case in test_cases_to_save:
        base_test_case = base_test_case_cls.model_validate(
            test_case.model_dump(mode="json")
        )
        data.append(
            base_test_case.model_dump(
                mode="json",
                by_alias=True,
                exclude_defaults=True,
            )
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open_atomic_text_file(output_path) as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
