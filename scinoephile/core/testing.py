#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to testing."""

from __future__ import annotations

from functools import partial
from os import getenv
from typing import Any

from pytest import fixture, mark, param

from scinoephile.common import package_root

__all__ = [
    "assert_expected_warnings",
    "flaky",
    "get_warning_messages",
    "parametrized_fixture",
    "skip_if_ci",
    "skip_if_codex",
    "test_data_root",
]


test_data_root = package_root.parent / "test" / "data"


def assert_expected_warnings(
    warnings: list[str], expected: list[str], label: str
) -> None:
    """Assert that warning messages match expected values.

    Arguments:
        warnings: warning messages captured during validation
        expected: expected warning messages
        label: label for error messages
    """
    if warnings != expected:
        formatted_actual = "\n".join(warnings)
        formatted_expected = "\n".join(expected)
        raise AssertionError(
            f"{label} warnings mismatch.\n"
            f"Expected:\n{formatted_expected}\n"
            f"Actual:\n{formatted_actual}"
        )


def get_warning_messages(records: list[Any]) -> list[str]:
    """Collect warning messages from captured log records.

    Arguments:
        records: log records captured during validation
    Returns:
        list of warning messages
    """
    return [record.getMessage() for record in records]


def flaky(inner: partial | None = None) -> partial:
    """Mark test as flaky (i.e., xfail but don’t fail suite on pass/fail).

    Arguments:
        inner: nascent partial function of pytest.param with additional marks
    Returns:
        partial function of pytest.param with marks
    """
    marks = [mark.xfail(strict=False, reason="Intentionally flaky test")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def parametrized_fixture(cls: type, params: list[dict[str, Any]]):
    """Decorator for parametrized test fixtures which provides clearer test output.

    Arguments:
        cls: stage fixture class
        params: fixture parameters
    Returns:
        fixture with provided params and clear ids
    """

    def get_name(args):
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture, params=params, ids=get_name)


def skip_if_ci(inner: partial | None = None) -> partial:
    """Mark test to skip if running within continuous integration pipeline.

    Arguments:
        inner: nascent partial function of pytest.param with additional marks
    Returns:
        partial function of pytest.param with marks
    """
    marks = [mark.skipif(getenv("CI") is not None, reason="Skip when running in CI")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)


def skip_if_codex(inner: partial | None = None) -> partial:
    """Mark test to skip if running within Codex environment.

    Arguments:
        inner: nascent partial function of pytest.param with additional marks
    Returns:
        partial function of pytest.param with marks
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
