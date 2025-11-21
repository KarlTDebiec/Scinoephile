#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 text."""

from __future__ import annotations

import re
from copy import deepcopy
from functools import cache

from opencc import OpenCC

from scinoephile.core.series import Series
from scinoephile.core.text import half_to_full_punc
from scinoephile.core.zhongwen.opencc_config import OpenCCConfig

conversion_exclusions = {
    "嗰": "𠮶",
    "纔": "才",
    "喫": "吃",
}


def get_zhongwen_cleaned(series: Series, remove_empty: bool = True) -> Series:
    """Get 中文 series cleaned.

    Arguments:
        series: Series to clean
        remove_empty: whether to remove subtitles with empty text
    Returns:
        Cleaned series
    """
    series = deepcopy(series)
    new_events = []
    for event in series:
        text = _get_zhongwen_text_cleaned(event.text.strip())
        if text or not remove_empty:
            event.text = text
            new_events.append(event)
    series.events = new_events
    return series


@cache
def get_zhongwen_converter(config: OpenCCConfig) -> OpenCC:
    """Get OpenCC converter for 中文 character set conversion.

    Arguments:
        config: OpenCC configuration
    Returns:
        OpenCC converter instance, from cache if available
    """
    return OpenCC(config)


def get_zhongwen_converted(
    series: Series,
    config: OpenCCConfig = OpenCCConfig.t2s,
    apply_exclusions: bool = True,
) -> Series:
    """Get 中文 converted between character sets.

    Arguments:
        series: Series to convert
        config: OpenCC configuration
        apply_exclusions: Whether to apply conversion exclusions
    Returns:
        Converted series
    """
    series = deepcopy(series)
    for event in series:
        event.text = get_zhongwen_text_converted(
            event.text, config, apply_exclusions=apply_exclusions
        )
    return series


def get_zhongwen_flattened(series: Series) -> Series:
    """Get multi-line 中文 series flattened to single lines.

    Arguments:
        series: Series to flatten
    Returns:
        Flattened series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_zhongwen_text_flattened(event.text)
    return series


def get_zhongwen_text_converted(
    text: str, config: OpenCCConfig, apply_exclusions: bool = True
) -> str:
    """Get 中文 text converted between character sets.

    Arguments:
        text: Text to convert
        config: OpenCC configuration for conversion
        apply_exclusions: Whether to apply conversion exclusions
    Returns:
        Converted text
    """
    converter = get_zhongwen_converter(config)
    converted_text = converter.convert(text)

    if apply_exclusions:
        if config in (
            OpenCCConfig.t2s,
            OpenCCConfig.tw2s,
            OpenCCConfig.hk2s,
            OpenCCConfig.tw2sp,
        ):
            for trad_char, simp_char in conversion_exclusions.items():
                if trad_char in text and simp_char in converted_text:
                    converted_text = converted_text.replace(simp_char, trad_char)
        if config in (
            OpenCCConfig.s2t,
            OpenCCConfig.s2tw,
            OpenCCConfig.s2hk,
            OpenCCConfig.s2twp,
        ):
            for trad_char, simp_char in conversion_exclusions.items():
                if simp_char in text and trad_char in converted_text:
                    converted_text = converted_text.replace(trad_char, simp_char)

    return converted_text


def _get_zhongwen_text_cleaned(text: str) -> str | None:
    """Get 中文 text cleaned.

    Arguments:
        text: Text to clean
    Returns:
        Cleaned text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    cleaned = re.sub(r"\\N", r"\n", text).strip()

    # Replace '...' with '⋯'
    cleaned = re.sub(r"[^\S\n]*\.\.\.[^\S\n]*", "⋯", cleaned)

    # Replace '…' with '⋯'
    cleaned = re.sub(r"[^\S\n]*…[^\S\n]*", "⋯", cleaned)

    # Replace half-width punctuation with full-width punctuation
    for old_punc, new_punc in half_to_full_punc.items():
        cleaned = re.sub(rf"[^\S\n]*{re.escape(old_punc)}[^\S\n]*", new_punc, cleaned)

    # Remove whitespace before and after specified characters
    cleaned = re.sub(r"[^\S\n]*([、「」『』《》])[^\S\n]*", r"\1", cleaned)

    # Remove empty lines but preserve newlines
    cleaned = re.sub(r"[ \t]*\n[ \t]*", "\n", cleaned)

    return cleaned


def _get_zhongwen_text_flattened(text: str) -> str:
    """Get multi-line 中文 text flattened to a single line.

    Accounts for dashes ('﹣') used for dialogue from multiple sources.

    # TODO: Consider replacing two western spaces with one eastern space

    Arguments:
        text: Text to flatten
    Returns:
        Flattened text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    flattened = re.sub(r"\\N", r"\n", text)

    # Merge lines
    flattened = re.sub(r"^(.+)\n(.+)$", r"\1　\2", flattened, flags=re.M)

    # Merge conversations
    conversation = re.match(
        r"^[-﹣]?[^\S\n]*(?P<first>.+)[\s]+[-﹣][^\S\n]*(?P<second>.+)$", flattened
    )
    if conversation is not None:
        flattened = (
            f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        )

    return flattened


__all__ = [
    "OpenCCConfig",
    "get_zhongwen_cleaned",
    "get_zhongwen_converted",
    "get_zhongwen_converter",
    "get_zhongwen_flattened",
    "get_zhongwen_text_converted",
]
