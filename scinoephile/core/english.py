#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""
from __future__ import annotations

import re
from logging import info

import nltk


def get_english_truecase(text: str) -> str:
    """Get truecased English text, useful for subtiltes stored in all capital letters.

    Arguments:
        text: text for which to get truecase
    Returns:
        truecased text
    """

    try:
        tagged = nltk.pos_tag([word.lower() for word in nltk.word_tokenize(text)])
    except LookupError:
        info("Downloading NLTK data")
        nltk.download("punkt")
        tagged = nltk.pos_tag([word.lower() for word in nltk.word_tokenize(text)])

    normalized = [w.capitalize() if t in ["NN", "NNS"] else w for (w, t) in tagged]
    normalized[0] = normalized[0].capitalize()

    truecased = re.sub(r" (?=[.,'!?:;])", "", " ".join(normalized))
    truecased = truecased.replace(" n't", "n't")
    truecased = truecased.replace(" i ", " I ")
    truecased = truecased.replace("``", '"')
    truecased = truecased.replace("''", '"')
    truecased = re.sub(
        r"(\A\w)|(?<!\.\w)([.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
        lambda s: s.group().upper(),
        truecased,
    )

    return truecased


def get_english_single_line_text(text: str) -> str:
    """Merge multi-line English text on a single line.

    Accounts for dashes ('-') used for dialogue from multiple sources.


    Arguments:
        text: text to merge
    Returns:
        merged text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    single_line = re.sub(r"\\N", r"\n", text)

    # Merge conversations
    single_line = re.sub(
        r"^\s*-\s*(.+)\n-\s*(.+)\s*$", r"- \1    - \2", single_line, re.M
    )

    # Merge lines
    single_line = re.sub(r"^\s*(.+)\s*\n\s*(.+)\s*$", r"\1 \2", single_line, re.M)

    return single_line
