#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Cantonese Chinese text."""

from __future__ import annotations

import pickle
import re
from collections import Counter
from copy import deepcopy
from logging import getLogger
from warnings import catch_warnings, filterwarnings, simplefilter

with catch_warnings():
    simplefilter("ignore", UserWarning)
    import pycantonese

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import full_to_half_punc, get_char_type, re_western
from scinoephile.lang.zho.conversion import get_zho_converter

__all__ = [
    "get_yue_romanized",
]

logger = getLogger(__name__)

data_root = package_root / "data/cantonese/"

# Load corpus
corpus_file_path = data_root / "corpus.pkl"
if corpus_file_path.exists():
    with open(corpus_file_path, "rb") as infile:
        corpus = pickle.load(infile)
else:
    with catch_warnings():
        filterwarnings("ignore", category=DeprecationWarning)
        corpus = pycantonese.hkcancor()
        # TODO: Load additional characters to corpus
        # corpus.add(data_root / "hanzi_to_jyutping.cha")
        with open(corpus_file_path, "wb") as outfile:
            pickle.dump(corpus, outfile, pickle.HIGHEST_PROTOCOL)

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
                elif re_western.match(char):
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
