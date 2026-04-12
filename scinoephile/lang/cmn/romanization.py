#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 普通话 text romanization."""

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
    "get_cmn_pinyin_query_strings",
    "get_cmn_romanized",
    "is_accented_pinyin_query",
]

RE_CMN_PINYIN = re.compile(
    r"^[A-Za-züÜvV:āáǎàēéěèīíǐìōóǒòūúǔù"
    r"ĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙêÊḿḾńŃňŇǹǸ]+[1-5]?$"
)


def get_cmn_pinyin_query_strings(text: str) -> list[str]:
    """Get normalized pinyin query strings for text.

    Arguments:
        text: Hanyu Pinyin query text with tone marks and optional apostrophes; tone
          numbers like ni3 hao3 are not accepted
    Returns:
        normalized pinyin query strings using tone numbers
    """
    text = (
        unicodedata.normalize("NFC", text).replace("’", "'").replace("'", " ").strip()
    )
    if not text:
        return []

    tokens = text.split()
    if not all(RE_CMN_PINYIN.fullmatch(token) for token in tokens):
        return []

    tokens = [tone_to_tone3(token.lower()).lower() for token in tokens]
    query_strings = {" ".join(tokens)}

    for query_string in tuple(query_strings):
        if "ü" in query_string:
            query_strings.add(query_string.replace("ü", "u:"))
            query_strings.add(query_string.replace("ü", "v"))
        if "u:" in query_string:
            query_strings.add(query_string.replace("u:", "ü"))
            query_strings.add(query_string.replace("u:", "v"))
        if "v" in query_string:
            query_strings.add(query_string.replace("v", "ü"))
            query_strings.add(query_string.replace("v", "u:"))

    return sorted(query_strings)


def is_accented_pinyin_query(text: str) -> bool:
    """Check whether text is accented Hanyu Pinyin.

    Arguments:
        text: query text
    Returns:
        whether text appears to be accented pinyin
    """
    normalized = (
        unicodedata.normalize("NFC", text).replace("’", "'").replace("'", " ").strip()
    )
    if not normalized:
        return False
    tokens = normalized.split()
    if any(token.lower().endswith("h") for token in tokens):
        return False
    if not get_cmn_pinyin_query_strings(text):
        return False
    # Use NFD so precomposed characters (e.g., ǎ) expose combining marks.
    return bool(
        re.search(
            r"[\u0300\u0301\u0302\u0304\u0308\u030C]",
            unicodedata.normalize("NFD", text),
        )
    )


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
