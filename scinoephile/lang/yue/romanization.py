#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Cantonese Chinese text."""

from __future__ import annotations

import pickle
import re
import unicodedata
from collections import Counter
from copy import deepcopy
from functools import cache, lru_cache
from logging import getLogger
from typing import cast
from warnings import catch_warnings, filterwarnings, simplefilter

with catch_warnings():
    simplefilter("ignore", UserWarning)
    import pycantonese


from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import RE_WESTERN, full_to_half_punc, get_char_type
from scinoephile.lang.zho.conversion import get_zho_converter

__all__ = [
    "get_yue_jyutping_variants",
    "get_yue_romanized",
]

logger = getLogger(__name__)

data_root = package_root / "data/yue/"
MAX_YUE_JYUTPING_VARIANTS = 16
RE_YALE_SEPARATOR = re.compile(r"[\s'’]+")
RE_YALE_TONE_MARK = re.compile(r"[\u0300\u0301\u0304]")
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
YUE_JYUTPING_TONES = ("1", "2", "3", "4", "5", "6")


def _build_corpus():
    """Build the Cantonese corpus and persist it to disk."""
    with catch_warnings():
        filterwarnings("ignore", category=DeprecationWarning)
        built_corpus = pycantonese.hkcancor()
    # TODO: Load additional characters to corpus
    # built_corpus.add(data_root / "hanzi_to_jyutping.cha")
    temp_corpus_file_path = corpus_file_path.with_suffix(".tmp")
    try:
        with open(temp_corpus_file_path, "wb") as outfile:
            pickle.dump(built_corpus, outfile, pickle.HIGHEST_PROTOCOL)
    except (TypeError, pickle.PickleError):
        temp_corpus_file_path.unlink(missing_ok=True)
    else:
        temp_corpus_file_path.replace(corpus_file_path)
    return built_corpus


# Load corpus
corpus_file_path = data_root / "corpus.pkl"
if corpus_file_path.exists():
    try:
        with open(corpus_file_path, "rb") as infile:
            corpus = pickle.load(infile)
    except (
        AttributeError,
        EOFError,
        ImportError,
        ModuleNotFoundError,
        pickle.PickleError,
    ):
        corpus_file_path.unlink(missing_ok=True)
        corpus = _build_corpus()
else:
    corpus = _build_corpus()

# Load Hanzi to Yale mapping
hanzi_to_romanization = {}
hanzi_to_yale_file_path = data_root / "hanzi_to_yale.pkl"
if hanzi_to_yale_file_path.exists():
    with open(hanzi_to_yale_file_path, "rb") as infile:
        hanzi_to_romanization = pickle.load(infile)

# Load unmatched Hanzi set
unmatched = set()
unmatched_hanzi_file_path = data_root / "unmatched_hanzi.pkl"
if unmatched_hanzi_file_path.exists():
    with open(unmatched_hanzi_file_path, "rb") as infile:
        unmatched = pickle.load(infile)

# Load Hanzi to Jyutping mapping
hanzi_to_jyutping = {}
hanzi_to_jyutping_path = data_root / "hanzi_to_jyutping.cha"
if hanzi_to_jyutping_path.exists():
    current_hanzi: str | None = None
    with open(hanzi_to_jyutping_path, encoding="utf-8") as infile:
        for raw_line in infile:
            line = raw_line.strip()
            if line.startswith("*XXA:"):
                current_hanzi = line.replace("*XXA:", "", 1).strip()
            elif line.startswith("%mor:") and current_hanzi is not None:
                entry = line.replace("%mor:", "", 1).strip()
                if "|" in entry:
                    _, jyutping = entry.split("|", 1)
                    hanzi_to_jyutping[current_hanzi] = jyutping.strip()
                current_hanzi = None

re_jyutping = re.compile(r"[a-z]+\\d")


def get_yue_jyutping_variants(text: str) -> list[str]:
    """Get normalized Jyutping search variants for text.

    Arguments:
        text: raw query text
    Returns:
        normalized Jyutping search variants
    """
    text = unicodedata.normalize("NFC", text).replace("’", "'").strip().lower()
    if not text:
        return []

    condensed = text.replace(" ", "")
    if "'" not in condensed:
        try:
            parsed = pycantonese.parse_jyutping(condensed)
        except ValueError:
            parsed = []
        if parsed:
            return [
                " ".join(
                    f"{syllable.onset}{syllable.nucleus}{syllable.coda}{syllable.tone}"
                    for syllable in parsed
                )
            ]

    if not _is_yale_query(text):
        return []
    return _get_yale_query_variants(text)


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


def _get_yale_query_variants(text: str) -> list[str]:
    """Get candidate Jyutping query variants from Yale text.

    Arguments:
        text: raw Yale query text
    Returns:
        candidate Jyutping query variants
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


def _is_yale_query(text: str) -> bool:
    """Check whether text appears to be Yale romanization.

    Arguments:
        text: raw query text
    Returns:
        whether text appears to be Yale romanization
    """
    if "'" in text:
        return True
    return RE_YALE_TONE_MARK.search(unicodedata.normalize("NFD", text)) is not None


def _get_yue_character_romanized(hanzi: str) -> str | None:  # noqa: PLR0912, PLR0915
    """Get the Yale Cantonese romanization of a single Chinese character.

    Arguments:
        hanzi: Chinese character
    Returns:
        Yale Cantonese romanization
    """
    if len(hanzi) != 1:
        raise ScinoephileError(
            "get_cantonese_character_romanization only accepts single Chinese character"
        )

    # If cached, use that value
    if hanzi in hanzi_to_romanization and hanzi_to_romanization[hanzi] is not None:
        return hanzi_to_romanization[hanzi]

    # If provided by mapping, use that value
    if hanzi in hanzi_to_jyutping:
        try:
            yale = pycantonese.jyutping_to_yale(hanzi_to_jyutping[hanzi])[0]
        except ValueError:
            yale = None
        if yale is not None:
            hanzi_to_romanization[hanzi] = yale
            with open(hanzi_to_yale_file_path, "wb") as outfile:
                pickle.dump(hanzi_to_romanization, outfile, pickle.HIGHEST_PROTOCOL)
        return yale

    # If known to be unmatched, stop early
    if hanzi in unmatched:
        return None

    # Otherwise search corpus for value
    matches = corpus.search(character=hanzi)
    jyutping: str | None = None
    yale: str | None = None

    # If not found, try traditional alternative
    if len(matches) == 0:
        trad_hanzi = get_zho_converter("s2t").convert(hanzi)
        if trad_hanzi != hanzi:
            yale = _get_yue_character_romanized(trad_hanzi)
        else:
            unmatched.add(hanzi)
            with open(unmatched_hanzi_file_path, "wb") as outfile:
                pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)

    # If found in corpus alone, use most common instance
    else:
        character_matches = [m.jyutping for m in matches if len(m.word) == 1]
        if len(character_matches) > 0:
            jyutping = Counter(character_matches).most_common(1)[0][0]

        # Otherwise use most common word
        else:
            try:
                most_common_word = Counter([m.word for m in matches]).most_common(1)[0][
                    0
                ]
                token = [m for m in matches if m.word == most_common_word][0]
                index = token.word.index(hanzi)
                jyutping_matches = re_jyutping.findall(token.jyutping)
                if index >= len(jyutping_matches):
                    unmatched.add(hanzi)
                    with open(unmatched_hanzi_file_path, "wb") as outfile:
                        pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
                    return None
                jyutping = jyutping_matches[index]
            except TypeError:
                unmatched.add(hanzi)
                with open(unmatched_hanzi_file_path, "wb") as outfile:
                    pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
                return None

        if jyutping is not None:
            try:
                yale = pycantonese.jyutping_to_yale(jyutping)[0]
            except ValueError:
                unmatched.add(hanzi)
                with open(unmatched_hanzi_file_path, "wb") as outfile:
                    pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)

    if yale is not None:
        hanzi_to_romanization[hanzi] = yale
        with open(hanzi_to_yale_file_path, "wb") as outfile:
            pickle.dump(hanzi_to_romanization, outfile, pickle.HIGHEST_PROTOCOL)
    return yale


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
            for char in section:
                if char in full_to_half_punc:
                    if char in {"＜", "＞"}:
                        section_romanization += char
                    else:
                        section_romanization += full_to_half_punc[char]
                elif RE_WESTERN.match(char):
                    section_romanization += char
                elif get_char_type(char) == "full":
                    romanization = _get_yue_character_romanized(char)
                    if romanization is not None:
                        section_romanization += " " + romanization
                    else:
                        logger.warning(
                            "No Cantonese romanization for character: %s", char
                        )
                        section_romanization += char
            line_romanization += "  " + section_romanization.strip()
        text_romanization += "\n" + line_romanization.strip()
    text_romanization = text_romanization.strip()

    return text_romanization
