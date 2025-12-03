#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Cantonese Chinese text."""

from __future__ import annotations

import pickle
import re
from collections import Counter
from copy import deepcopy
from warnings import catch_warnings, filterwarnings

import pycantonese
from opencc import OpenCC

from scinoephile.common import package_root
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.series import Series
from scinoephile.core.text import full_to_half_punc, get_char_type, re_western

_s2t = OpenCC("s2t")

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

re_jyutping = re.compile(r"[a-z]+\d")


def get_cantonese_romanization(series: Series) -> Series:
    """Get the Yale Cantonese romanization of a Chinese series.

    Arguments:
        series: Series for which to get Yale Cantonese romanization
    Returns:
        Yale Cantonese romanization of series
    """
    series = deepcopy(series)
    for event in series:
        event.text = _get_cantonese_text_romanization(event.text)
    return series


def _get_cantonese_character_romanization(hanzi: str) -> str | None:
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

    # If known to be unmatched, stop early
    if hanzi in unmatched:
        return None

    # If cached, use that value
    elif hanzi in hanzi_to_romanization:
        return hanzi_to_romanization[hanzi]

    # Otherwise search corpus for value
    matches = corpus.search(character=hanzi)
    jyutping: str | None = None
    yale: str | None = None

    # If not found, try traditional alternative
    if len(matches) == 0:
        trad_hanzi = _s2t.convert(hanzi)
        if trad_hanzi != hanzi:
            yale = _get_cantonese_character_romanization(trad_hanzi)
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
                jyutping = re_jyutping.findall(token.jyutping)[index]
            except TypeError:
                unmatched.add(hanzi)
                with open(unmatched_hanzi_file_path, "wb") as outfile:
                    pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)

        if jyutping is not None:
            try:
                yale = pycantonese.jyutping_to_yale(jyutping)[0]
            except ValueError:
                unmatched.add(hanzi)
                with open(unmatched_hanzi_file_path, "wb") as outfile:
                    pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)

    hanzi_to_romanization[hanzi] = yale
    with open(hanzi_to_yale_file_path, "wb") as outfile:
        pickle.dump(hanzi_to_romanization, outfile, pickle.HIGHEST_PROTOCOL)
    return yale


def _get_cantonese_text_romanization(text: str) -> str:
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
                    section_romanization += full_to_half_punc[char]
                elif re_western.match(char):
                    section_romanization += char
                elif get_char_type(char) == "full":
                    romanization = _get_cantonese_character_romanization(char)
                    if romanization is not None:
                        section_romanization += " " + romanization
                    else:
                        section_romanization += char
            line_romanization += "  " + section_romanization.strip()
        text_romanization += "\n" + line_romanization.strip()
    text_romanization = text_romanization.strip()

    return text_romanization


__all__ = [
    "get_cantonese_romanization",
]
