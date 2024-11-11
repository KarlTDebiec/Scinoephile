#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Cantonese Chinese text."""
from __future__ import annotations

import pickle
import re
from collections import Counter
from copy import deepcopy
from warnings import catch_warnings, filterwarnings

import pycantonese
from hanziconv import HanziConv

from scinoephile.common import package_root
from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.series import Series
from scinoephile.core.text import punctuation, re_hanzi, re_hanzi_rare, re_western

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
hanzi_to_pinyin = {}
hanzi_to_yale_file_path = data_root / "hanzi_to_yale.pkl"
if hanzi_to_yale_file_path.exists():
    with open(hanzi_to_yale_file_path, "rb") as infile:
        hanzi_to_pinyin = pickle.load(infile)

# Load unmatched Hanzi set
unmatched = set()
unmatched_hanzi_file_path = data_root / "unmatched_hanzi.pkl"
if unmatched_hanzi_file_path.exists():
    with open(unmatched_hanzi_file_path, "rb") as infile:
        unmatched = pickle.load(infile)

re_jyutping = re.compile(r"[a-z]+\d")


def get_cantonese_pinyin_character(hanzi: str) -> str:
    """Get the Yale Cantonese romanization of a single Hanzi.

    Arguments:
        hanzi: Hanzi
    Returns:
        Yale Cantonese romanization
    """
    if len(hanzi) != 1:
        raise ScinoephileException(
            "get_cantonese_pinyin_for_single_hanzi only accepts single hanzi"
        )

    # If known to be unmatched, stop early
    if hanzi in unmatched:
        return None

    # If cached, use that value
    elif hanzi in hanzi_to_pinyin:
        return hanzi_to_pinyin[hanzi]

    # Otherwise search corpus for value
    matches = corpus.search(character=hanzi)

    # If not found, try traditional alternative
    if len(matches) == 0:
        trad_hanzi = HanziConv.toTraditional(hanzi)
        if trad_hanzi != hanzi:
            yale = get_cantonese_pinyin_character(trad_hanzi)
            hanzi_to_pinyin[hanzi] = yale
            with open(hanzi_to_yale_file_path, "wb") as outfile:
                pickle.dump(hanzi_to_pinyin, outfile, pickle.HIGHEST_PROTOCOL)
            return yale

        # Truly no instance of hanzi in corpus
        unmatched.add(hanzi)
        with open(unmatched_hanzi_file_path, "wb") as outfile:
            pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
        return None

    # If found in corpus alone, use most common instance
    character_matches = [m.jyutping for m in matches if len(m.word) == 1]
    if len(character_matches) > 0:
        jyutping = Counter(character_matches).most_common(1)[0][0]

    # Otherwise use most common word
    else:
        try:
            most_common_word = Counter([m.word for m in matches]).most_common(1)[0][0]
            token = [m for m in matches if m.word == most_common_word][0]
            index = token.word.index(hanzi)
            jyutping = re_jyutping.findall(token.jyutping)[index]
        except TypeError:
            unmatched.add(hanzi)
            with open(unmatched_hanzi_file_path, "wb") as outfile:
                pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
            return None

    # Convert from jyutping to yale
    try:
        yale = pycantonese.jyutping2yale(jyutping)[0]
        hanzi_to_pinyin[hanzi] = yale
        with open(hanzi_to_yale_file_path, "wb") as outfile:
            pickle.dump(hanzi_to_pinyin, outfile, pickle.HIGHEST_PROTOCOL)
        return yale
    except ValueError:
        unmatched.add(hanzi)
        with open(unmatched_hanzi_file_path, "wb") as outfile:
            pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
        return None


def get_cantonese_pinyin_series(series: Series) -> Series:
    """Get the Yale Cantonese romanization of Hanzi series.

    Arguments:
        series: series for which to get Yale Cantonese romanization
    Returns:
        Yale Cantonese romanization of series
    """
    series = deepcopy(series)
    for subtitle in series:
        subtitle.text = get_cantonese_pinyin_text(subtitle.text)
    return series


def get_cantonese_pinyin_text(text: str) -> str:
    """Get the Yale Cantonese romanization of Hanzi text.

    Arguments:
        text: Hanzi text
    Returns:
        Yale Cantonese romanization
    """
    romanization = ""
    for line in text.split("\n"):
        line_romanization = ""
        for section in line.split():
            section_romanization = ""
            for char in section:
                if char in punctuation:
                    section_romanization += punctuation[char]
                elif re_western.match(char):
                    section_romanization += char
                elif re_hanzi.match(char) or re_hanzi_rare.match(char):
                    pinyin = get_cantonese_pinyin_character(char)
                    if pinyin is not None:
                        section_romanization += " " + pinyin
                    else:
                        section_romanization += char
            line_romanization += "  " + section_romanization.strip()
        romanization += "\n" + line_romanization.strip()
    romanization = romanization.strip()

    return romanization
