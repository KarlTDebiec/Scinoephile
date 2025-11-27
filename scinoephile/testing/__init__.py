#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to testing."""

from __future__ import annotations

import asyncio
import re
from functools import partial
from importlib.util import module_from_spec, spec_from_file_location
from logging import info
from os import getenv
from pathlib import Path
from typing import Any

from pytest import fixture, mark, param

from scinoephile.common import package_root
from scinoephile.common.validation import val_output_path
from scinoephile.core.abcs import DynamicLLMQueryer, FixedLLMQueryer, TestCase
from scinoephile.core.abcs.llm_queryer import LLMQueryer
from scinoephile.testing.sync_test_case import SyncTestCase

test_data_root = package_root.parent / "test" / "data"


async def _replace_variable_in_test_case_file(
    path: Path, variable: str, pattern: re.Pattern[str], replacement: str
):
    contents = await asyncio.to_thread(path.read_text, encoding="utf-8")
    block = f"{variable} = {replacement}  # {variable}"
    new_contents = pattern.sub(lambda _m: block, contents)
    await asyncio.to_thread(path.write_text, new_contents, encoding="utf-8")
    info(f"Replaced test cases {variable} in {path.name}.")


def flaky(inner: partial | None = None) -> partial:
    """Mark test as flaky (i.e., xfail but don’t fail suite on pass/fail).

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.xfail(strict=False, reason="Intentionally flaky test")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def get_test_cases_from_file_path(
    test_case_path: Path,
) -> list[TestCase]:
    """Get test cases from file path.

    Arguments:
        test_case_path: path to file containing test cases
    Returns:
        test cases
    """
    test_case_path = val_output_path(test_case_path, exist_ok=True)
    if not test_case_path.exists():
        return []
    spec = spec_from_file_location("test_cases", test_case_path)
    if spec is None:
        return []
    module = module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        return []
    loader.exec_module(module)

    test_cases = []
    for name in getattr(module, "__all__", []):
        if name.endswith("test_cases"):
            if value := getattr(module, name, None):
                test_cases.extend(value)
    return test_cases


def parametrized_fixture(cls: type, params: list[dict[str, Any]]):
    """Decorator for parametrized test fixtures which provides clearer test output.

    Arguments:
        cls: Stage fixture class
        params: Fixture parameters
    Returns:
        Fixture with provided params and clear ids
    """

    def get_name(args):
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture(params=params, ids=get_name))


def skip_if_ci(inner: partial | None = None) -> partial:
    """Mark test to skip if running within continuous integration pipeline.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.skipif(getenv("CI") is not None, reason="Skip when running in CI")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def skip_if_codex(inner: partial | None = None) -> partial:
    """Mark test to skip if running within Codex environment.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [
        mark.skipif(
            getenv("CODEX_ENV_PYTHON_VERSION") is not None,
            reason="Skip when running in Codex environment",
        )
    ]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


async def update_test_cases(path: Path, variable: str, queryer: LLMQueryer):
    """Update test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test cases
        queryer: LLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=\s*\[(.*?)\]  # {variable}", re.DOTALL)
    replacement = queryer.encountered_test_cases_source_str
    await _replace_variable_in_test_case_file(path, variable, pattern, replacement)
    await asyncio.to_thread(queryer.clear_encountered_test_cases)


async def update_dynamic_test_cases(
    path: Path, variable: str, queryer: DynamicLLMQueryer
):
    """Update dynamic test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test case
        queryer: DynamicLLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=(.*?)# {variable}", re.DOTALL)
    replacement = queryer.encountered_test_cases_source_str
    await _replace_variable_in_test_case_file(path, variable, pattern, replacement)
    await asyncio.to_thread(queryer.clear_encountered_test_cases)


__all__ = [
    "SyncTestCase",
    "flaky",
    "get_test_cases_from_file_path",
    "parametrized_fixture",
    "skip_if_ci",
    "skip_if_codex",
    "test_data_root",
    "update_dynamic_test_cases",
    "update_test_cases",
]
