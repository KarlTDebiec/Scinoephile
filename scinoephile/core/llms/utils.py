#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utility helpers for LLM test cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path
from typing import cast

from pydantic import TypeAdapter, ValidationError

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
    # Prepare prompt-specific test-case classes
    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    test_case_cls = manager_cls.get_test_case_cls(prompt)

    # Load serialized test cases
    with open(input_path, encoding="utf-8") as input_file:
        raw_test_cases: object = json.load(input_file)

    # Validate using the base-prompt schema. Unverified generated answers may become
    # stale as semantic validators improve; retain their valid queries for replacement.
    raw_test_case_adapter = TypeAdapter(list[dict[str, object]])
    raw_test_case_items = raw_test_case_adapter.validate_python(
        raw_test_cases, strict=True
    )
    base_test_cases: list[TTestCase] = []
    stale_answer_count = 0
    for raw_test_case in raw_test_case_items:
        try:
            base_test_case = base_test_case_cls.model_validate(
                raw_test_case,
                by_alias=True,
                by_name=False,
                strict=True,
                extra="forbid",
                context={"alias_only": True},
            )
        except ValidationError as original_error:
            if (
                raw_test_case.get("answer") is None
                or raw_test_case.get("verified") is True
                or raw_test_case.get("few_shot") is True
                or any(
                    flag_name in raw_test_case
                    and not isinstance(raw_test_case[flag_name], bool)
                    for flag_name in ("few_shot", "verified")
                )
            ):
                raise
            unanswered_test_case_data = {
                **raw_test_case,
                "answer": None,
                "few_shot": False,
                "verified": False,
            }
            try:
                base_test_case = base_test_case_cls.model_validate(
                    unanswered_test_case_data,
                    by_alias=True,
                    by_name=False,
                    strict=True,
                    extra="forbid",
                    context={"alias_only": True},
                )
            except ValidationError:
                raise original_error
            stale_answer_count += 1
        base_test_cases.append(cast("TTestCase", base_test_case))
    if stale_answer_count:
        logger.warning(
            f"Discarded {stale_answer_count} stale unverified answer(s) while "
            f"loading {input_path}; their valid queries will be regenerated."
        )

    # Convert to the requested prompt schema
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
    test_cases_to_save = list(test_cases)
    base_test_case_cls = manager_cls.get_test_case_cls(manager_cls.base_prompt)
    base_test_case_list_type = list[base_test_case_cls]
    base_test_case_adapter = TypeAdapter(base_test_case_list_type)
    data = base_test_case_adapter.dump_python(
        test_cases_to_save, mode="json", by_alias=True, exclude_defaults=True
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open_atomic_text_file(output_path) as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
