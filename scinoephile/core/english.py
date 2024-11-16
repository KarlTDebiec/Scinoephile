#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to English text."""
from __future__ import annotations

import re
from copy import deepcopy
from logging import info

import nltk

from scinoephile.core.series import Series


def get_english_series_merged_to_single_line(series: Series) -> Series:
    """Get multi-line English series merged to single lines.

    Arguments:
        series: series to merge
    Returns:
        merged series
    """
    series = deepcopy(series)
    for subtitle in series:
        subtitle.text = get_english_text_merged_to_single_line(subtitle.text.strip())
    return series


def get_english_series_truecased(series: Series) -> Series:
    """Get all-caps English series truecased.

    Arguments:
        series: series to truecase
    Returns:
        truecased series
    """
    series = deepcopy(series)
    for subtitle in series:
        subtitle.text = get_english_text_truecased(subtitle.text)
    return series


def get_english_text_merged_to_single_line(text: str) -> str:
    """Get multi-line English text merged to a single line.

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
        r"^\s*-\s*(.+)\n-\s*(.+)\s*$",
        lambda m: f"- {m.group(1).strip()}    - {m.group(2).strip()}",
        single_line,
        flags=re.M,
    )

    # Merge lines
    single_line = re.sub(
        r"^\s*(.+)\s*\n\s*(.+)\s*$",
        lambda m: f"{m.group(1).strip()} {m.group(2).strip()}",
        single_line,
        flags=re.M,
    )
    return single_line


def get_english_text_truecased(text: str) -> str:
    """Get all-caps English text truecased.

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
