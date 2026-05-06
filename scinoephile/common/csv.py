#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CSV parsing utilities."""

from __future__ import annotations

__all__ = [
    "parse_csv_int_list",
    "parse_csv_str_list",
]


def parse_csv_int_list(values: str, *, name: str) -> list[int]:
    """Parse a comma-separated integer list.

    Arguments:
        values: comma-separated integer values
        name: argument name for error context
    Returns:
        list of parsed integers
    """
    parsed_values: list[int] = []
    for item in values.split(","):
        value = item.strip()
        if value == "":
            continue
        try:
            parsed_values.append(int(value))
        except ValueError as exc:
            raise ValueError(f"Invalid integer {value!r} in {name}") from exc
    if not parsed_values:
        raise ValueError(f"{name} must include at least one integer")
    return parsed_values


def parse_csv_str_list(values: str | None) -> list[str]:
    """Parse a comma-separated string list.

    Arguments:
        values: comma-separated string values
    Returns:
        list of parsed strings with whitespace stripped and empty entries removed
    """
    if values is None or values.strip() == "":
        return []
    return [item.strip() for item in values.split(",") if item.strip()]
