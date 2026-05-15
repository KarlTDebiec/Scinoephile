#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for cache CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError
from datetime import timedelta
from pathlib import Path

from scinoephile.core.cache.duration import parse_duration
from scinoephile.core.paths import get_runtime_cache_dir_path

__all__ = [
    "cache_dir_path_arg",
    "duration_arg",
]


def cache_dir_path_arg(*values: str | None) -> Path:
    """Resolve a cache directory CLI argument.

    Arguments:
        *values: path value or runtime cache subpath parts
    Returns:
        resolved cache directory path
    """
    if len(values) == 0 or values == (None,):
        return get_runtime_cache_dir_path(create=False)
    if len(values) > 1:
        parts = [value for value in values if value is not None]
        return get_runtime_cache_dir_path(*parts, create=False)
    value = values[0]
    if value is None:
        return get_runtime_cache_dir_path(create=False)
    return Path(value).expanduser().resolve()


def duration_arg(value: str) -> timedelta:
    """Parse a duration CLI argument.

    Arguments:
        value: duration string
    Returns:
        parsed duration
    Raises:
        ArgumentTypeError: if duration parsing fails
    """
    try:
        return parse_duration(value)
    except ValueError as exc:
        raise ArgumentTypeError(str(exc)) from exc
