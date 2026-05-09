#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese script analysis functions."""

from __future__ import annotations

from scinoephile.core.text import RE_HANZI
from scinoephile.lang.zho.conversion import OpenCCConfig, get_zho_text_converted

from .result import ZhoScriptAnalysis

__all__ = ["get_zho_script_analysis"]

MIN_DECISIVE_CHARACTERS = 2
"""Minimum number of script-specific characters needed for detection."""
MIN_DECISIVE_RATIO = 4
"""Minimum ratio of one script-specific count to the other."""


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
    if is_decisively_greater(simplified_count, traditional_count):
        script = "zho-Hans"
    elif is_decisively_greater(traditional_count, simplified_count):
        script = "zho-Hant"

    return ZhoScriptAnalysis(
        script=script,
        simplified_count=simplified_count,
        traditional_count=traditional_count,
        shared_count=shared_count,
    )


def is_decisively_greater(count: int, opposite_count: int) -> bool:
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
