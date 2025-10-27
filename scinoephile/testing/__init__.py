#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to testing."""

from __future__ import annotations

import asyncio
import re
from functools import partial
from logging import info
from os import getenv
from pathlib import Path
from typing import Any

from pytest import fixture, mark, param

from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.common import package_root
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.abcs import DynamicLLMQueryer, FixedLLMQueryer
from scinoephile.testing.sync_test_case import SyncTestCase

test_data_root = package_root.parent / "test" / "data"


async def _replace(
    path: Path, varible: str, pattern: re.Pattern[str], replacement: str
):
    contents = await asyncio.to_thread(path.read_text, encoding="utf-8")
    replacement = f"{varible} = {replacement}  # {varible}"
    replacement = replacement.replace("\\n", "\\\\n")
    new_contents = pattern.sub(replacement, contents)
    await asyncio.to_thread(path.write_text, new_contents, encoding="utf-8")
    info(f"Replaced test cases {varible} in {path.name}.")


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


async def update_test_cases(path: Path, variable: str, queryer: FixedLLMQueryer):
    """Update test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test cases
        queryer: LLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=\s*\[(.*?)\]  # {variable}", re.DOTALL)
    replacement = queryer.encountered_test_cases_source_str
    await _replace(path, variable, pattern, replacement)
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
    await _replace(path, variable, pattern, replacement)
    await asyncio.to_thread(queryer.clear_encountered_test_cases)


__all__ = [
    "SyncTestCase",
    "flaky",
    "parametrized_fixture",
    "skip_if_ci",
    "skip_if_codex",
    "test_data_root",
    "update_dynamic_test_cases",
    "update_test_cases",
]
