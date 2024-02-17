#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to Cantonese Chinese text."""
from __future__ import annotations, annotations

import pickle
import re
from collections import Counter
from warnings import catch_warnings, filterwarnings

import pycantonese
from hanziconv import HanziConv

from scinoephile.common import package_root
from scinoephile.core.exception import ScinoephileException
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

# Load hanzi to yale mapping
hanzi_to_pinyin = {}
hanzi_to_yale_file_path = data_root / "hanzi_to_yale.pkl"
if hanzi_to_yale_file_path.exists():
    with open(hanzi_to_yale_file_path, "rb") as infile:
        hanzi_to_pinyin = pickle.load(infile)

# Load unmatched hanzi set
unmatched = set()
unmatched_hanzi_file_path = data_root / "unmatched_hanzi.pkl"
if unmatched_hanzi_file_path.exists():
    with open(unmatched_hanzi_file_path, "rb") as infile:
        unmatched = pickle.load(infile)

re_jyutping = re.compile(r"[a-z]+\d")


def get_cantonese_pinyin(text: str) -> str:
    """Get the Yale Cantonese romanization of hanzi text.

    Arguments:
        text: hanzi text
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
                    pinyin = get_cantonese_pinyin_for_single_hanzi(char)
                    if pinyin is not None:
                        section_romanization += " " + pinyin
                    else:
                        section_romanization += char
            line_romanization += "  " + section_romanization.strip()
        romanization += "\n" + line_romanization.strip()
    romanization = romanization.strip()

    return romanization


def get_cantonese_pinyin_for_single_hanzi(hanzi: str) -> str:
    """Get the Yale Cantonese romanization of a single hanzi.

    Arguments:
        hanzi: hanzi chinese character
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
            yale = get_cantonese_pinyin_for_single_hanzi(trad_hanzi)
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
    character_matches = [m[2] for m in matches if len(m[0]) == 1]
    if len(character_matches) > 0:
        jyutping = Counter(character_matches).most_common(1)[0][0]

    # Otherwise use most common word
    else:
        most_common_word = Counter(matches).most_common(1)[0][0]
        index = most_common_word[0].index(hanzi)
        jyutping = re_jyutping.findall(most_common_word[2])[index]

    # Convert from jyutping to yale
    try:
        yale = pycantonese.jyutping2yale(jyutping)
        hanzi_to_pinyin[hanzi] = yale
        with open(hanzi_to_yale_file_path, "wb") as outfile:
            pickle.dump(hanzi_to_pinyin, outfile, pickle.HIGHEST_PROTOCOL)
        return yale
    except ValueError:
        unmatched.add(hanzi)
        with open(unmatched_hanzi_file_path, "wb") as outfile:
            pickle.dump(unmatched, outfile, pickle.HIGHEST_PROTOCOL)
        return None
