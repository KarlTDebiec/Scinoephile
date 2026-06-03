#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to written Cantonese text romanization."""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from logging import getLogger
from typing import Any

import pycantonese

from scinoephile.core.subtitles import Series
from scinoephile.core.text import RE_WESTERN, full_to_half_punc, get_char_type
from scinoephile.lang.zho.script.conversion import get_zho_converter

__all__ = [
    "get_yue_jyutping_query_strings",
    "get_yue_romanized",
    "get_yue_text_romanized",
    "is_accented_yale",
    "is_numbered_jyutping",
]

logger = getLogger(__name__)

RE_YALE_PROHIBITED_CHARACTERS = re.compile(r"[üÜ:]")
RE_YALE_TONE_MARK = re.compile(r"[\u0300\u0301\u0304]")


def get_yue_jyutping_query_strings(text: str) -> list[str]:
    """Get normalized Jyutping query strings for text.

    Arguments:
        text: raw query text
    Returns:
        normalized Jyutping query strings
    """
    text = _normalize_yue_romanization_query_text(text)
    if not text:
        return []

    parsed = _parse_normalized_jyutping(text)
    if parsed:
        return [
            " ".join(
                f"{syllable.onset}{syllable.nucleus}{syllable.coda}{syllable.tone}"
                for syllable in parsed
            )
        ]

    if "'" not in text and not is_accented_yale(text):
        return []
    try:
        return pycantonese.yale_to_jyutping(text)
    except ValueError:
        return []


def get_yue_romanized(series: Series, append: bool = True) -> Series:
    """Get the Yale Cantonese romanization of a Chinese series.

    Arguments:
        series: Series for which to get Yale Cantonese romanization
        append: Whether to append romanization to original text
    Returns:
        Yale Cantonese romanization of series
    """
    series = deepcopy(series)
    for event in series:
        romanized = get_yue_text_romanized(event.text)
        if append:
            if romanized:
                event.text = f"{event.text}\\N{romanized}"
        else:
            event.text = romanized
    return series


def is_accented_yale(text: str) -> bool:
    """Check whether text appears to be Yale romanization.

    Arguments:
        text: raw query text
    Returns:
        whether text appears to be Yale romanization
    """
    normalized = unicodedata.normalize("NFC", text).strip()
    if not normalized:
        return False
    if RE_YALE_PROHIBITED_CHARACTERS.search(normalized) is not None:
        return False
    return (
        RE_YALE_TONE_MARK.search(unicodedata.normalize("NFD", normalized)) is not None
    )


def is_numbered_jyutping(text: str) -> bool:
    """Check whether text appears to be numbered Jyutping.

    Arguments:
        text: query text
    Returns:
        whether text appears to be numbered Jyutping
    """
    normalized = _normalize_yue_romanization_query_text(text)
    if not normalized:
        return False
    return bool(_parse_normalized_jyutping(normalized))


def get_yue_text_romanized(text: str) -> str:
    """Get the Yale Cantonese romanization of Chinese text.

    Arguments:
        text: Chinese text
    Returns:
        Yale Cantonese romanization
    """
    text_romanization = ""
    for line in text.split("\n"):
        line_romanization = ""
        for section in line.split():
            section_romanization = ""
            index = 0
            while index < len(section):
                char = section[index]
                if char in full_to_half_punc:
                    if char in {"＜", "＞"}:
                        section_romanization += char
                    else:
                        section_romanization += full_to_half_punc[char]
                    index += 1
                elif RE_WESTERN.match(char):
                    section_romanization += char
                    index += 1
                elif get_char_type(char) == "full":
                    end_index = index + 1
                    while (
                        end_index < len(section)
                        and get_char_type(section[end_index]) == "full"
                    ):
                        end_index += 1
                    hanzi_run = section[index:end_index]
                    hanzi_run_romanization = _romanize_yue_hanzi_run(hanzi_run)
                    if hanzi_run_romanization[:1] != hanzi_run[:1]:
                        section_romanization += " "
                    section_romanization += hanzi_run_romanization
                    index = end_index
                else:
                    index += 1
            line_romanization += "  " + section_romanization.strip()
        text_romanization += "\n" + line_romanization.strip()
    return text_romanization.strip()


def _jyutping_to_yale(jyutping: str) -> str | None:
    """Convert numbered Jyutping to space-delimited Yale romanization.

    Arguments:
        jyutping: numbered Jyutping
    Returns:
        Yale romanization or None if conversion fails
    """
    normalized = _normalize_yue_romanization_query_text(jyutping)
    if not normalized:
        return None
    parsed = _parse_normalized_jyutping(normalized)
    if not parsed:
        return None
    normalized_jyutping = " ".join(
        f"{syllable.onset}{syllable.nucleus}{syllable.coda}{syllable.tone}"
        for syllable in parsed
    )
    try:
        return " ".join(pycantonese.jyutping_to_yale(normalized_jyutping))
    except ValueError:
        return None


def _normalize_yue_romanization_query_text(text: str) -> str:
    """Normalize text for Yale and Jyutping query parsing.

    Arguments:
        text: raw query text
    Returns:
        normalized query text
    """
    return unicodedata.normalize("NFC", text).replace("’", "'").strip().lower()


def _parse_normalized_jyutping(text: str) -> tuple[Any, ...]:
    """Parse normalized Jyutping text.

    Arguments:
        text: normalized Jyutping text
    Returns:
        parsed Jyutping syllables, or an empty tuple if parsing fails
    """
    condensed = text.replace(" ", "").replace("'", "")
    try:
        return tuple(pycantonese.parse_jyutping(condensed))
    except ValueError:
        return ()


def _romanize_yue_hanzi_run(text: str) -> str:
    """Romanize a contiguous Hanzi run with PyCantonese segmentation.

    Arguments:
        text: contiguous Hanzi text
    Returns:
        Yale romanization with unmatched chunks preserved
    """
    trad_text = get_zho_converter("s2t").convert(text)
    segments = pycantonese.segment(trad_text, offsets=True)
    jyutping_segments = pycantonese.characters_to_jyutping(
        [segment for segment, _ in segments]
    )

    pieces: list[tuple[str, bool]] = []
    for (_, (start, end)), (_, jyutping) in zip(
        segments, jyutping_segments, strict=True
    ):
        original_segment = text[start:end]
        if jyutping is None:
            for char in original_segment:
                logger.warning(f"No Cantonese romanization for character: {char}")
            pieces.append((original_segment, True))
            continue

        yale = _jyutping_to_yale(jyutping)
        if yale is None:
            for char in original_segment:
                logger.warning(f"No Cantonese romanization for character: {char}")
            pieces.append((original_segment, True))
            continue
        pieces.append((yale, False))

    output = ""
    for piece, is_raw in pieces:
        if output and not is_raw:
            output += " "
        output += piece
    return output
