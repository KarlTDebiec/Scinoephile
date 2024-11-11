#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Mandarin Chinese text."""
from __future__ import annotations

from copy import deepcopy

from pypinyin import pinyin
from snownlp import SnowNLP

from scinoephile.core.subtitle_series import SubtitleSeries
from scinoephile.core.text import punctuation


def get_mandarin_pinyin_subtitles(subtitles: SubtitleSeries) -> SubtitleSeries:
    """Get the Mandarin pinyin romanization of Hanzi subtitles.

    Arguments:
        subtitles: Subtitles for which to get Mandarin pinyin romanization
    Returns:
        Mandarin pinyin romanization of subtitles
    """
    subtitles = deepcopy(subtitles)
    for subtitle in subtitles:
        subtitle.text = get_mandarin_pinyin_text(subtitle.text)
    return subtitles


def get_mandarin_pinyin_text(text: str) -> str:
    """Get the Mandarin pinyin romanization of Hanzi text.

    Arguments:
        text: Hanzi text
    Returns:
        Mandarin pinyin romanization
    """
    romanization = ""
    for line in text.split("\n"):
        line_romanization = ""
        for section in line.split():
            section_romanization = ""
            for word in SnowNLP(section).words:
                if word in punctuation:
                    section_romanization += punctuation[word]
                else:
                    section_romanization += " " + "".join([a[0] for a in pinyin(word)])
            line_romanization += "  " + section_romanization.strip()
        romanization += "\n" + line_romanization.strip()
    romanization = romanization.strip()

    return romanization
