#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Testing support utilities shared by runtime and tests."""

from __future__ import annotations

from typing import Any

from scinoephile.common import package_root

__all__ = [
    "assert_expected_warnings",
    "get_warning_messages",
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
