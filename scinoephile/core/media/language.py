#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media language tag helpers."""

from __future__ import annotations

from typing import TypeGuard

__all__ = ["is_chinese"]

_CHINESE_LANGUAGE_CODES = {"chi", "zho", "yue"}
"""Language codes treated as Chinese for script analysis."""


def is_chinese(language: str | None) -> TypeGuard[str]:
    """Return whether a language tag should be treated as Chinese.

    Arguments:
        language: language tag, if available
    Returns:
        whether the language tag is Chinese
    """
    if language is None:
        return False
    return language.split("-", 1)[0].lower() in _CHINESE_LANGUAGE_CODES
