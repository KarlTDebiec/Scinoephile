#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to models."""

from __future__ import annotations

import textwrap
from typing import Any


def format_field(name: str, value: object) -> str:
    """Format a field for source representation.

    Arguments:
        name: Name of the field
        value: Value of the field
    Returns:
        Formatted string representation of the field
    """

    def get_wrapped_lines(value: str) -> list[str]:
        if len(value) <= 60:
            return [value]
        wrapped_lines = textwrap.wrap(
            value,
            width=60,
            break_long_words=False,
            break_on_hyphens=False,
        )
        # Add a trailing space to all but the last line
        for i in range(len(wrapped_lines) - 1):
            wrapped_lines[i] += " "
        return wrapped_lines

    if not isinstance(value, str):
        return f"    {name}={value!r},"

    if value == "":
        return f'    {name}="",'

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    wrapped_sections = []
    escaped_lines = escaped.splitlines()
    for escaped_line in escaped_lines:
        wrapped_lines = get_wrapped_lines(escaped_line)
        wrapped_sections += [wrapped_lines]
    # Add a trailing newline to all but the last section
    for i in range(len(wrapped_sections) - 1):
        wrapped_sections[i][-1] += "\\n"
    final_lines = [line for section in wrapped_sections for line in section]

    final = (
        "\n".join(
            [f'    {name}="{final_lines[0]}"']
            + [f'    {" " * (len(name) + 1)}"{line}"' for line in final_lines[1:]]
        )
        + ","
    )
    return final


def make_hashable(value: Any) -> Any:
    """Make a value hashable for use in keys.

    Arguments:
        value: Value to make hashable
    Returns:
        Hashable representation of the value
    """
    if isinstance(value, list):
        return tuple(make_hashable(v) for v in value)
    elif isinstance(value, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
    return value


__all__ = [
    "format_field",
    "make_hashable",
]
