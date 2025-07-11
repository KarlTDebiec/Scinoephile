#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to hanzi text."""

from __future__ import annotations

import re
from copy import deepcopy
from enum import Enum
from functools import lru_cache

from opencc import OpenCC

from scinoephile.core.series import Series
from scinoephile.core.text import half_to_full_punc

half_to_full_punc_for_cleaning = deepcopy(half_to_full_punc)
half_to_full_punc_for_cleaning["-"] = "﹣"
half_to_full_punc_for_cleaning["－"] = "﹣"


class OpenCCConfig(str, Enum):
    """OpenCC configuration names for hanzi character set conversion."""

    s2t = "s2t"
    """Simplified Chinese to Traditional Chinese.
    
    簡體到繁體
    """
    t2s = "t2s"
    """Traditional Chinese to Simplified Chinese.
    
    繁體到簡體
    """
    s2tw = "s2tw"
    """Simplified Chinese to Traditional Chinese (Taiwan).
    
    簡體到臺灣正體
    """
    tw2s = "tw2s"
    """Traditional Chinese (Taiwan) to Simplified Chinese.
    
    臺灣正體到簡體.
    """
    s2hk = "s2hk"
    """Simplified Chinese to Traditional Chinese (Hong Kong).
    
    簡體到香港繁體
    """
    hk2s = "hk2s"
    """Traditional Chinese (Hong Kong) to Simplified Chinese.
    
    香港繁體到簡體
    """
    s2twp = "s2twp"
    """Simplified Chinese to Traditional Chinese (Taiwan) with Taiwanese idiom.
    
    簡體到繁體（臺灣正體標準）並轉換爲臺灣常用詞彙
    """
    tw2sp = "tw2sp"
    """Traditional Chinese (Taiwan) to Simplified Chinese with Mainland Chinese idiom.
    
    繁體（臺灣正體標準）到簡體並轉換爲中國大陸常用詞彙
    """
    t2tw = "t2tw"
    """Traditional Chinese (OpenCC) to Taiwan Standard.
    
    繁體（OpenCC 標準）到臺灣正體
    """
    hk2t = "hk2t"
    """Traditional Chinese (Hong Kong) to Traditional Chinese.
    
    香港繁體到繁體（OpenCC 標準）
    """
    t2hk = "t2hk"
    """Traditional Chinese (OpenCC) to Hong Kong variant.
    
    繁體（OpenCC 標準）到香港繁體
    """
    t2jp = "t2jp"
    """Traditional Chinese Characters (Kyūjitai) to New Japanese Kanji (Shinjitai).
    
    繁體（OpenCC 標準，舊字體）到日文新字體
    """
    jp2t = "jp2t"
    """New Japanese Kanji (Shinjitai) to Traditional Chinese Characters (Kyūjitai).
    
    日文新字體到繁體（OpenCC 標準，舊字體）
    """
    tw2t = "tw2t"
    """Traditional Chinese (Taiwan) to Traditional Chinese.
    
    臺灣正體到繁體（OpenCC 標準）
    """


def get_hanzi_cleaned(series: Series) -> Series:
    """Get hanzi series cleaned.

    Arguments:
        series: Series to clean
    Returns:
        Cleaned series
    """
    series = deepcopy(series)
    new_events = []
    for event in series.events:
        text = _get_hanzi_text_cleaned(event.text.strip())
        if text:
            event.text = text
            new_events.append(event)
    series.events = new_events
    return series


@lru_cache
def get_hanzi_converter(config: OpenCCConfig) -> OpenCC:
    """Get OpenCC converter for hanzi character set conversion.

    Arguments:
        config: OpenCC configuration name
    Returns:
        OpenCC converter instance, from cache if available
    """
    return OpenCC(config)


def get_hanzi_flattened(series: Series) -> Series:
    """Get multi-line hanzi series flattened to single lines.

    Arguments:
        series: Series to flatten
    Returns:
        Flattened series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_hanzi_text_flattened(event.text)
    return series


def get_hanzi_converted(series: Series, config: str = "t2s") -> Series:
    """Get hanzi converted between character sets.

    Arguments:
        series: Series to convert
        config: Conversion name
    Returns:
        Converted series
    """
    series = deepcopy(series)
    for event in series:
        event.text = get_hanzi_converter(config).convert(event.text)
    return series


def _get_hanzi_text_cleaned(text: str) -> str | None:
    """Get hanzi text cleaned.

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
    for old_punc, new_punc in half_to_full_punc_for_cleaning.items():
        cleaned = re.sub(rf"[^\S\n]*{re.escape(old_punc)}[^\S\n]*", new_punc, cleaned)

    # Remove whitespace before and after specified characters
    cleaned = re.sub(r"[^\S\n]*([、「」『』《》])[^\S\n]*", r"\1", cleaned)

    # Remove empty lines but preserve newlines
    cleaned = re.sub(r"[ \t]*\n[ \t]*", "\n", cleaned)

    return cleaned


def _get_hanzi_text_flattened(text: str) -> str:
    """Get multi-line hanzi text flattened to a single line.

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
    "get_hanzi_cleaned",
    "get_hanzi_converted",
    "get_hanzi_converter",
    "get_hanzi_flattened",
    "half_to_full_punc_for_cleaning",
]
