#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to hanzi text."""
from __future__ import annotations

import re
from copy import deepcopy

from hanziconv import HanziConv

from scinoephile.core.series import Series

re_hanzi = re.compile(r"[\u4e00-\u9fff]")
re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")


def get_hanzi_cleaned(series: Series) -> Series:
    """Get hanzi series cleaned.

    Arguments:
        series: series to clean
    Returns:
        cleaned series
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


def get_hanzi_flattened(series: Series) -> Series:
    """Get multi-line hanzi series flattened to single lines.

    Arguments:
        series: series to flatten
    Returns:
        flattened series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_hanzi_text_flattened(event.text)
    return series


def get_hanzi_simplified(series: Series) -> Series:
    """Get traditional hanzi series simplified.

    Arguments:
        series: series to simplify
    Returns:
        simplified series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_hanzi_text_simplified(event.text)
    return series


def get_hanzi_traditionalized(series: Series) -> Series:
    """Get simplified hanzi series traditionalized.

    Arguments:
        series: series to traditionalize
    Returns:
        traditionalized series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_hanzi_text_tradionalized(event.text)
    return series


def _get_hanzi_text_cleaned(text: str) -> str | None:
    """Get hanzi text cleaned.

    Arguments:
        text: text to clean
    Returns:
        cleaned text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    cleaned = re.sub(r"\\N", r"\n", text).strip()

    # Replace '...' with '⋯'
    cleaned = re.sub(r"\.\.\.", "⋯", cleaned)

    # Replace '…' with '⋯'
    cleaned = re.sub(r"\s*…\s*", "⋯", cleaned)

    # Replace ',' with '，'
    cleaned = re.sub(r"\s*,\s*", "，", cleaned)

    # Replace '!' with '！'
    cleaned = re.sub(r"\s*!\s*", "！", cleaned)

    # Replace '?' with '？'
    cleaned = re.sub(r"\s*\?\s*", "？", cleaned)

    # Replace '~' with '～'
    cleaned = re.sub(r"\s*~\s*", "～", cleaned)

    # Remove whitespace before and after specified characters
    cleaned = re.sub(r"\s*([、「」『』《》])\s*", r"\1", cleaned)

    # Remove empty lines
    cleaned = re.sub(r"\s*\n\s*", "\n", cleaned)

    # Check if any substantive text remains
    if not cleaned:
        return None
    if re.fullmatch(r"^\s*-?\s*\n\s*-?\s*", cleaned):
        return None

    return cleaned


def _get_hanzi_text_flattened(text: str) -> str:
    """Get multi-line hanzi text flattened to a single line.

    Accounts for dashes ('﹣') used for dialogue from multiple sources.

    # TODO: Consider replacing two western spaces with one eastern space

    Arguments:
        text: text to flatten
    Returns:
        flattened text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    flattened = re.sub(r"\\N", r"\n", text)

    # Merge lines
    flattened = re.sub(r"^(.+)\n(.+)$", r"\1　\2", flattened, re.M)

    # Merge conversations
    conversation = re.match(
        r"^[-﹣]?\s*(?P<first>.+)[\s]+[-﹣]\s*(?P<second>.+)$", flattened
    )
    if conversation is not None:
        flattened = (
            f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        )

    return flattened


def _get_hanzi_text_simplified(text: str) -> str:
    """Get traditional hanzi text simplified.

    Arguments:
        text: text to simplify
    Returns:
        simplified text
    """
    simplified = ""

    for char in text:
        if re_hanzi.match(char) or re_hanzi_rare.match(char):
            simplified += HanziConv.toSimplified(char)
        else:
            simplified += char

    return simplified


def _get_hanzi_text_tradionalized(text: str) -> str:
    """Get simplified hanzi text traditionalized.

    Arguments:
        text: text to traditionalize
    Returns:
        traditionalized text
    """
    traditionalized = ""

    exclusions = {"出", "了", "札", "面", "向", "只", "志", "疴"}
    # TODO: 疴 to 痾?

    for char in text:
        if re_hanzi.match(char) or re_hanzi_rare.match(char):
            if char in exclusions:
                traditionalized += char
            traditionalized += HanziConv.toTraditional(char)
        else:
            traditionalized += char

    return traditionalized
