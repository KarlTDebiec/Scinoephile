#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to models."""

from __future__ import annotations

from typing import Any


def format_field(name: str, value: object) -> str:
    """Format a field for source representation.

    Arguments:
        name: Name of the field
        value: Value of the field
    Returns:
        Formatted string representation of the field
    """
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'    {name}="{escaped}",'
    return f"    {name}={value!r},"


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
