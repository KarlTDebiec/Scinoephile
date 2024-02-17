#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Mandarin Chinese text."""
from __future__ import annotations

from pypinyin import pinyin
from snownlp import SnowNLP

from scinoephile.core.text import punctuation


def get_mandarin_pinyin(text: str) -> str:
    """Get the pinyin romanization of hanzi text.

    Arguments:
        text: hanzi text
    Returns:
        pinyin romanization
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
