#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for Scinoephile CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError

__all__ = ["language_arg"]


def language_arg(value: object) -> str:
    """Validate an ISO language code argument.

    Arguments:
        value: value to validate
    Returns:
        normalized language code
    Raises:
        ArgumentTypeError: if value is not a non-empty string
    """
    language = str(value).strip().lower()
    if not language:
        raise ArgumentTypeError("language code may not be empty")
    return language
