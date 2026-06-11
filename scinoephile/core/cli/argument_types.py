#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for Scinoephile CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError

from scinoephile.core.language import normalize_language_tag

__all__ = ["language_arg"]


def language_arg(value: object) -> str:
    """Validate a loose language tag argument.

    Arguments:
        value: value to validate
    Returns:
        normalized language tag
    Raises:
        ArgumentTypeError: if value is not a language tag
    """
    try:
        return normalize_language_tag(str(value))
    except ValueError as exc:
        raise ArgumentTypeError(str(exc)) from exc
