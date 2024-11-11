#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to hanzi text."""
from __future__ import annotations

import re
from copy import deepcopy

from hanziconv import HanziConv

from scinoephile.core.series import Series

re_hanzi = re.compile(r"[\u4e00-\u9fff]")
re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")


def get_hanzi_series_simplified(series: Series) -> Series:
    """Get traditional hanzi series simplified.

    Arguments:
        series: series to simplify
    Returns:
        simplified series
    """
    series = deepcopy(series)
    for subtitle in series:
        subtitle.text = get_hanzi_text_simplified(subtitle.text)
    return series


def get_hanzi_series_merged_to_single_line(series: Series) -> Series:
    """Get multi-line hanzi series merged to single lines.

    Arguments:
        series: series to merge
    Returns:
        merged series
    """
    series = deepcopy(series)
    for subtitle in series:
        subtitle.text = get_hanzi_text_merged_to_single_line(subtitle.text)
    return series


def get_hanzi_text_merged_to_single_line(text: str) -> str:
    """Get multi-line hanzi text merged to a single line.

    Accounts for dashes ('﹣') used for dialogue from multiple sources.

    # TODO: Consider replacing two western spaces with one eastern space

    Arguments:
        text: text to merge
    Returns:
        merged text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    single_line = re.sub(r"\\N", r"\n", text)

    # Merge lines
    single_line = re.sub(r"^(.+)\n(.+)$", r"\1　\2", single_line, re.M)

    # Merge conversations
    conversation = re.match(
        r"^[-﹣]?\s*(?P<first>.+)[\s]+[-﹣]\s*(?P<second>.+)$", single_line
    )
    if conversation is not None:
        single_line = (
            f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        )

    return single_line


def get_hanzi_text_simplified(text: str) -> str:
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
