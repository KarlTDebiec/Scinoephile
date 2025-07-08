#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Mandarin Chinese text."""

from __future__ import annotations

from copy import deepcopy

import jieba
from pypinyin import pinyin

from scinoephile.core.series import Series
from scinoephile.core.text import full_to_half_punc


def get_mandarin_romanization(series: Series) -> Series:
    """Get the Mandarin pinyin romanization of Hanzi series.

    Arguments:
        series: Series for which to get Mandarin pinyin romanization
    Returns:
        Mandarin pinyin romanization of series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_mandarin_text_romanization(event.text)
    return series


def _get_mandarin_text_romanization(text: str) -> str:
    """Get the Mandarin pinyin romanization of Hanzi text.

    Arguments:
        text: Hanzi text
    Returns:
        Mandarin pinyin romanization
    """
    text_romanization = ""
    for line in text.split("\n"):
        line_romanization = ""
        for section in line.split():
            section_romanization = ""
            for word in jieba.cut(section):
                if word in full_to_half_punc:
                    section_romanization += full_to_half_punc[word]
                else:
                    section_romanization += " " + "".join([a[0] for a in pinyin(word)])
            line_romanization += "  " + section_romanization.strip()
        text_romanization += "\n" + line_romanization.strip()
    text_romanization = text_romanization.strip()

    return text_romanization


__all__ = [
    "get_mandarin_romanization",
]
