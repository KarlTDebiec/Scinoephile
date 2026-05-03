#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 text romanization."""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from functools import cache, lru_cache
from logging import getLogger
from typing import Any, cast
from warnings import catch_warnings, simplefilter

with catch_warnings():
    simplefilter("ignore", UserWarning)
    import pycantonese

from scinoephile.core.subtitles import Series
from scinoephile.core.text import RE_WESTERN, full_to_half_punc, get_char_type
from scinoephile.lang.zho.conversion import get_zho_converter

__all__ = [
    "get_yue_jyutping_query_strings",
    "get_yue_romanized",
    "is_accented_yale",
    "is_numbered_jyutping",
    "yale_to_jyutping",
]

logger = getLogger(__name__)

MAX_YUE_JYUTPING_VARIANTS = 16
RE_YALE_PROHIBITED_CHARACTERS = re.compile(r"[üÜ:]")
RE_YALE_SEPARATOR = re.compile(r"[\s'’]+")
RE_YALE_TONE_MARK = re.compile(r"[\u0300\u0301\u0304]")
YUE_JYUTPING_CODAS = (
    "p",
    "t",
    "k",
    "m",
    "n",
    "ng",
    "i",
    "u",
    "",
)
YUE_JYUTPING_NUCLEI = (
    "aa",
    "a",
    "i",
    "yu",
    "u",
    "oe",
    "e",
    "eo",
    "o",
    "m",
    "ng",
)
YUE_JYUTPING_ONSETS = (
    "b",
    "d",
    "g",
    "gw",
    "z",
    "p",
    "t",
    "k",
    "kw",
    "c",
    "m",
    "n",
    "ng",
    "f",
    "h",
    "s",
    "l",
    "w",
    "j",
    "",
)
YUE_JYUTPING_TONES = ("1", "2", "3", "4", "5", "6")


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
    return yale_to_jyutping(text)


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
        romanized = _get_yue_text_romanized(event.text)
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


def yale_to_jyutping(text: str) -> list[str]:
    """Get candidate Jyutping query strings from Yale text.

    Arguments:
        text: raw Yale query text
    Returns:
        candidate Jyutping query strings
    """
    chunks = [chunk for chunk in RE_YALE_SEPARATOR.split(text) if chunk]
    variants: list[tuple[str, ...]] = [()]
    for chunk in chunks:
        chunk_variants = _get_yale_chunk_variants(chunk)
        if not chunk_variants:
            return []

        new_variants: list[tuple[str, ...]] = []
        for prefix in variants:
            for suffix in chunk_variants:
                candidate = prefix + suffix
                if candidate not in new_variants:
                    new_variants.append(candidate)
                    if len(new_variants) >= MAX_YUE_JYUTPING_VARIANTS:
                        break
            if len(new_variants) >= MAX_YUE_JYUTPING_VARIANTS:
                break
        variants = new_variants

    return [" ".join(variant) for variant in variants]


def _get_yale_chunk_variants(chunk: str) -> list[tuple[str, ...]]:
    """Get candidate Jyutping syllable tuples for one Yale chunk.

    Arguments:
        chunk: Yale query chunk without spaces or apostrophes
    Returns:
        candidate Jyutping syllable tuples
    """
    yale_syllables, yale_to_jyutping = _get_yale_jyutping_syllables()

    @cache
    def _parse_chunk(remaining: str) -> tuple[tuple[str, ...], ...]:
        """Parse remaining Yale text into shortest Jyutping syllable variants.

        Arguments:
            remaining: Yale text remaining to parse
        Returns:
            shortest candidate Jyutping syllable tuples
        """
        if not remaining:
            return ((),)

        variants: list[tuple[str, ...]] = []
        best_len: int | None = None
        for yale_syllable in yale_syllables:
            if not remaining.startswith(yale_syllable):
                continue

            for remainder_variant in _parse_chunk(remaining[len(yale_syllable) :]):
                candidate_len = 1 + len(remainder_variant)
                if best_len is not None and candidate_len > best_len:
                    continue

                for jyutping_syllable in yale_to_jyutping[yale_syllable]:
                    if best_len is None or candidate_len < best_len:
                        variants = []
                        best_len = candidate_len

                    candidate = (jyutping_syllable, *remainder_variant)
                    if candidate not in variants:
                        variants.append(candidate)
                        if len(variants) >= MAX_YUE_JYUTPING_VARIANTS:
                            return tuple(variants)

        return tuple(variants)

    return list(_parse_chunk(chunk))


@lru_cache(maxsize=1)
def _get_yale_jyutping_syllables() -> tuple[
    tuple[str, ...], dict[str, tuple[str, ...]]
]:
    """Get Yale-to-Jyutping single-syllable mappings.

    Returns:
        Yale syllables in descending-length order and Jyutping mapping
    """
    yale_to_jyutping: dict[str, set[str]] = {}
    for onset in YUE_JYUTPING_ONSETS:
        for nucleus in YUE_JYUTPING_NUCLEI:
            for coda in YUE_JYUTPING_CODAS:
                for tone in YUE_JYUTPING_TONES:
                    jyutping = f"{onset}{nucleus}{coda}{tone}"
                    try:
                        parsed = pycantonese.parse_jyutping(jyutping)
                    except ValueError:
                        continue
                    if len(parsed) != 1:
                        continue

                    try:
                        yale = pycantonese.jyutping_to_yale(
                            jyutping, return_as="string"
                        )
                    except (KeyError, ValueError):
                        continue
                    yale_to_jyutping.setdefault(yale, set()).add(jyutping)

    sorted_mapping: dict[str, tuple[str, ...]] = {
        yale: tuple(sorted(variants, key=lambda value: (-len(value), value)))
        for yale, variants in yale_to_jyutping.items()
    }
    sorted_yale_syllables = cast(
        tuple[str, ...],
        tuple(sorted(sorted_mapping, key=len, reverse=True)),
    )
    return sorted_yale_syllables, sorted_mapping


def _get_yue_text_romanized(text: str) -> str:
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
        return " ".join(
            pycantonese.jyutping_to_yale(syllable, return_as="string")
            for syllable in normalized_jyutping.split()
        )
    except (KeyError, ValueError):
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
                logger.warning("No Cantonese romanization for character: %s", char)
            pieces.append((original_segment, True))
            continue

        yale = _jyutping_to_yale(jyutping)
        if yale is None:
            for char in original_segment:
                logger.warning("No Cantonese romanization for character: %s", char)
            pieces.append((original_segment, True))
            continue
        pieces.append((yale, False))

    output = ""
    for piece, is_raw in pieces:
        if output and not is_raw:
            output += " "
        output += piece
    return output
