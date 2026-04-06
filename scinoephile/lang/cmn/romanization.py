#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Mandarin Chinese text."""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from warnings import catch_warnings, simplefilter

with catch_warnings():
    simplefilter("ignore", SyntaxWarning)
    import jieba
from typing import TYPE_CHECKING

from pypinyin import pinyin
from pypinyin.contrib.tone_convert import tone_to_tone3

from scinoephile.core.text import full_to_half_punc

if TYPE_CHECKING:
    from scinoephile.core.subtitles import Series

__all__ = [
    "get_cmn_pinyin_variants",
    "get_cmn_romanized",
]

RE_CMN_PINYIN_TOKEN = re.compile(
    r"^[A-Za-züÜvV:āáǎàēéěèīíǐìōóǒòūúǔù"
    r"ĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙêÊḿḾńŃňŇǹǸ]+[1-5]?$"
)


def get_cmn_pinyin_variants(text: str) -> list[str]:
    """Get normalized pinyin search variants for text.

    Arguments:
        text: raw query text
    Returns:
        normalized pinyin search variants
    """
    text = (
        unicodedata.normalize("NFC", text).replace("’", "'").replace("'", " ").strip()
    )
    if not text:
        return []

    tokens = text.split()
    if not all(RE_CMN_PINYIN_TOKEN.fullmatch(token) for token in tokens):
        return []

    return [
        " ".join(
            tone_to_tone3(token.lower(), v_to_u=True).lower().replace("ü", "u:")
            for token in tokens
        )
    ]


def get_cmn_romanized(series: Series, append: bool = True) -> Series:
    """Get the Mandarin pinyin romanization of Hanzi series.

    Arguments:
        series: Series for which to get Mandarin pinyin romanization
        append: Whether to append romanization to original text
    Returns:
        Mandarin pinyin romanization of series
    """
    series = deepcopy(series)
    for event in series:
        romanized = _get_cmn_text_romanized(event.text)
        if append:
            if romanized:
                event.text = f"{event.text}\\N{romanized}"
        else:
            event.text = romanized
    return series


def _get_cmn_text_romanized(text: str) -> str:
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
                    if word in {"＜", "＞"}:
                        section_romanization += word
                    else:
                        section_romanization += full_to_half_punc[word]
                else:
                    section_romanization += " " + "".join([a[0] for a in pinyin(word)])
            line_romanization += "  " + section_romanization.strip()
        text_romanization += "\n" + line_romanization.strip()
    text_romanization = text_romanization.strip()

    return text_romanization
