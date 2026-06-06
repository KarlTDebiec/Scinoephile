#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for cache CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError
from datetime import timedelta

from scinoephile.cli.cache import cache_dir_path_arg
from scinoephile.core.cache.duration import parse_duration

__all__ = [
    "cache_dir_path_arg",
    "duration_arg",
]


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
