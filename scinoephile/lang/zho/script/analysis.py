#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese script analysis functions."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.text import RE_HANZI

from .conversion import OpenCCConfig, get_zho_text_converted

__all__ = [
    "ZhoScriptAnalysis",
    "get_zho_script_analysis",
    "is_simplified",
    "is_traditional",
]

MIN_DECISIVE_CHARACTERS = 2
"""Minimum number of script-specific characters needed for detection."""
MIN_DECISIVE_RATIO = 4
"""Minimum ratio of one script-specific count to the other."""


@dataclass(frozen=True)
class ZhoScriptAnalysis:
    """Chinese script analysis result."""

    script: str | None
    """Detected BCP-47 Chinese script tag, when determined."""
    simplified_count: int
    """Number of simplified-only Hanzi observed."""
    traditional_count: int
    """Number of traditional-only Hanzi observed."""
    shared_count: int
    """Number of Hanzi that do not distinguish simplified from traditional."""


def get_zho_script_analysis(text: str) -> ZhoScriptAnalysis:
    """Analyze whether Chinese text uses simplified or traditional characters.

    Arguments:
        text: text to analyze
    Returns:
        Chinese script analysis
    """
    simplified_count = 0
    traditional_count = 0
    shared_count = 0

    for match in RE_HANZI.finditer(text):
        char = match.group(0)
        simplified_char = get_zho_text_converted(
            char,
            OpenCCConfig.t2s,
            apply_exclusions=False,
        )
        traditional_char = get_zho_text_converted(
            char,
            OpenCCConfig.s2t,
            apply_exclusions=False,
        )
        if char != simplified_char:
            traditional_count += 1
        elif char != traditional_char:
            simplified_count += 1
        else:
            shared_count += 1

    script = None
    if _is_decisively_greater(simplified_count, traditional_count):
        script = "zho-Hans"
    elif _is_decisively_greater(traditional_count, simplified_count):
        script = "zho-Hant"

    return ZhoScriptAnalysis(
        script=script,
        simplified_count=simplified_count,
        traditional_count=traditional_count,
        shared_count=shared_count,
    )


def is_simplified(text: str) -> bool:
    """Check whether text is simplified Chinese.

    Arguments:
        text: text to classify
    Returns:
        whether text is simplified Chinese
    """
    if RE_HANZI.search(text) is None:
        return False
    simplified = get_zho_text_converted(
        text,
        OpenCCConfig.t2s,
        apply_exclusions=False,
    )
    return text == simplified


def is_traditional(text: str) -> bool:
    """Check whether text is traditional Chinese.

    Arguments:
        text: text to classify
    Returns:
        whether text is traditional Chinese
    """
    if RE_HANZI.search(text) is None:
        return False
    traditional = get_zho_text_converted(
        text,
        OpenCCConfig.s2t,
        apply_exclusions=False,
    )
    return text == traditional


def _is_decisively_greater(count: int, opposite_count: int) -> bool:
    """Return whether a script-specific count is decisive.

    Arguments:
        count: script-specific character count
        opposite_count: opposite script-specific character count
    Returns:
        whether the count is decisive
    """
    if count < MIN_DECISIVE_CHARACTERS:
        return False
    if opposite_count == 0:
        return True
    return count >= opposite_count * MIN_DECISIVE_RATIO
