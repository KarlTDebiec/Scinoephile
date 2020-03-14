#!python
#   scinoephile.core.text.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import re
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd

from scinoephile.core import SubtitleSeries

################################## VARIABLES ##################################
punctuation = {"\n": "\n",
               "　": " ",
               " ": " ",
               "？": "?",
               "，": ",",
               "、": ",",
               ".": ".",
               "！": "!",
               "…": "...",
               "...": "...",
               "﹣": "-",
               "─": "─",
               "-": "-",
               "“": "\"",
               "”": "\"",
               "\"": "\"",
               "《": "<",
               "》": ">",
               "「": "[",
               "」": "]",
               "：": ":"}
re_hanzi = re.compile(r"[\u4e00-\u9fff]")
re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")
re_western = re.compile(r"[a-zA-Z0-9]")


################################## FUNCTIONS ##################################
def format_list(list_of_strings: List[str], linker: str = "and",
                quote: str = "'") -> str:
    # TODO: Document
    string = quote + f"{quote}, {quote}".join(list_of_strings) + quote
    if len(list_of_strings) == 2:
        string = re.sub(r"(.*), ", rf"\1 {linker} ", string)
    elif len(list_of_strings) > 2:
        string = re.sub(r"(.*), ", rf"\1, {linker} ", string)
    return string


def get_simplified_hanzi(text: str, verbosity: int = 1) -> str:
    """
    Converts traditional hanzi to simplified

    Args:
        text (str): Text to simplify

    Returns:
        str: Text with traditional hanzi exchanged for simplified
    """
    from hanziconv import HanziConv

    simplified = ""
    for char in text:
        if re_hanzi.match(char) or re_hanzi_rare.match(char):
            simplified += HanziConv.toSimplified(char)
        else:
            simplified += char
    if verbosity >= 2:
        print(f"{text} -> {simplified}")
    return simplified


def get_pinyin(text: str, language: str = "mandarin",
               verbosity: int = 1) -> str:
    """
    Converts hanzi to pinyin

    Args:
        text (str): Text to convert
        language (str): Language of pinyin to use; may be 'mandarin' or
          'cantonese'
        verbosity (int): Level of verbose output

    Returns:
        str: Pinyin text
    """
    if language == "mandarin":
        from snownlp import SnowNLP
        from pypinyin import pinyin

        romanization = ""
        for line in text.split("\n"):
            line_romanization = ""
            for section in line.split():
                section_romanization = ""
                for word in SnowNLP(section).words:
                    if word in punctuation:
                        section_romanization += punctuation[word]
                    else:
                        section_romanization += " " + "".join(
                            [a[0] for a in pinyin(word)])
                line_romanization += "  " + section_romanization.strip()
            romanization += "\n" + line_romanization.strip()
        romanization = romanization.strip()

    elif language == "cantonese":
        from scinoephile.cantonese import get_cantonese_pinyin

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
                        pinyin = get_cantonese_pinyin(char)
                        if pinyin is not None:
                            section_romanization += " " + pinyin
                        else:
                            section_romanization += char
                line_romanization += "  " + section_romanization.strip()
            romanization += "\n" + line_romanization.strip()
        romanization = romanization.strip()
    else:
        raise ValueError("Invalid value provided for argument 'language'; "
                         "must of 'cantonese' or 'mandarin'")
    if verbosity >= 2:
        print(f"{text} -> {romanization}")
    return romanization


def get_truecase(text: str) -> str:
    """
    Converts English text to truecase.

    Useful for subtiltes stored in all capital letters

    Args:
        text (str): Text to apply truecase to

    Returns:
        str: Text with truecase
    """
    import nltk

    tagged = nltk.pos_tag([word.lower() for word in nltk.word_tokenize(text)])
    normalized = [w.capitalize() if t in ["NN", "NNS"] else w for (w, t) in
                  tagged]
    normalized[0] = normalized[0].capitalize()
    truecased = re.sub(r" (?=[.,'!?:;])", "", " ".join(normalized))
    truecased = truecased.replace(" n't", "n't")
    truecased = truecased.replace(" i ", " I ")
    truecased = truecased.replace("``", "\"")
    truecased = truecased.replace("''", "\"")
    truecased = re.sub(r"(\A\w)|(?<!\.\w)([.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
                       lambda s: s.group().upper(), truecased)
    return truecased


def get_single_line_text(text: str, language: str = "english") -> str:
    """
    Arranges multi-line text on a single line.

    Accounts for dashes ('-') used for dialogue from multiple sources

    Args:
        text (str): Text to arrange
        language (str): Punctuation and spacing language to use; may be
          'english', 'hanzi', or 'pinyin'

    Returns:
        str: Text arranged on a single line
    """
    # TODO: Consider replacing two western spaces with one eastern space

    # Revert strange substitution in pysubs2/subrip.py:66
    single_line = re.sub(r"\\N", r"\n", text)
    if language == "english" or language == "pinyin":
        single_line = re.sub(r"^\s*-\s*(.+)\n-\s*(.+)\s*$",
                             r"- \1    - \2",
                             single_line, re.M)
        single_line = re.sub(r"^\s*(.+)\s*\n\s*(.+)\s*$",
                             r"\1 \2",
                             single_line, re.M)
    elif language == "hanzi":
        single_line = re.sub(r"^\s*(.+)\s*\n\s*(.+)\s*$",
                             r"\1　\2",
                             single_line, re.M)
        single_line = re.sub(r"^\s*﹣?\s*(.+)\s+﹣(.+)\s*$",
                             r"﹣\1　　﹣\2",
                             single_line, re.M)
    else:
        raise ValueError("Invalid value for argument 'language'; must be "
                         "'english', 'hanzi', or 'pinyin'")

    return single_line


def merge_subtitles(upper: Any, lower: Any) -> pd.DataFrame:
    """
    Merges and synchronizes two sets of subtitles.

    Args:
        upper (SubtitleSeries, pandas.DataFrame): Upper subtitles
        lower (SubtitleSeries, pandas.DataFrame): Lower subtitles

    Returns:
        DataFrame: Merged and synchronized subtitles
    """

    def add_event(merged: List[Tuple[int, int, str]]) -> None:
        if start != time:
            if upper_text is None:
                merged += [pd.DataFrame.from_records(
                    [(start, time, lower_text)],
                    columns=["start", "end", "lower text"])]
            elif lower_text is None:
                merged += [pd.DataFrame.from_records(
                    [(start, time, upper_text)],
                    columns=["start", "end", "upper text"])]
            else:
                merged += [pd.DataFrame.from_records(
                    [(start, time, upper_text, lower_text)],
                    columns=["start", "end", "upper text", "lower text"])]

    # Process arguments
    if isinstance(upper, SubtitleSeries):
        upper = upper.get_dataframe()
    if isinstance(lower, SubtitleSeries):
        lower = lower.get_dataframe()

    # Organize transitions
    # TODO: Validate that events within each series do not overlap
    transitions: List[Tuple[int, str, Optional[str]]] = []
    for _, event in upper.iterrows():
        transitions += [(event["start"], "upper_start", event["text"]),
                        (event["end"], "upper_end", None)]
    for _, event in lower.iterrows():
        transitions += [(event["start"], "lower_start", event["text"]),
                        (event["end"], "lower_end", None)]
    transitions.sort()

    # Merge events
    merged: List[Tuple[int, int, str]] = []
    start = upper_text = lower_text = None
    for time, kind, text in transitions:
        if kind == "upper_start":
            if start is None:
                # Transition from __ -> C_
                pass
            else:
                # Transition from _E -> CE
                add_event(merged)
            upper_text = text
            start = time
        elif kind == "upper_end":
            add_event(merged)
            upper_text = None
            if lower_text is None:
                # Transition from C_ -> __
                start = None
            else:
                # Transition from CE -> _C
                start = time
        elif kind == "lower_start":
            if start is None:
                # Transition from __ -> _E
                pass
            else:
                # Transition from C_ -> CE
                add_event(merged)
            lower_text = text
            start = time
        elif kind == "lower_end":
            add_event(merged)
            lower_text = None
            if upper_text is None:
                # Transition from _E -> __
                start = None
            else:
                # Transition from CE -> E_
                start = time
    merged_df = pd.concat(merged, sort=False, ignore_index=True)[
        ["upper text", "lower text", "start", "end"]]

    # Synchronize events
    synced_list = [merged_df.iloc[0].copy()]
    for index in range(1, merged_df.shape[0]):
        last = synced_list[-1]
        next = merged_df.iloc[index].copy()
        if last["upper text"] == next["upper text"]:
            if isinstance(last["lower text"], float) and np.isnan(
                    last["lower text"]):
                # Upper started before lower
                last["lower text"] = next["lower text"]
                last["end"] = next["end"]
            elif isinstance(next["lower text"], float) and np.isnan(
                    next["lower text"]):
                # Lower started before upper
                last["end"] = next["end"]
            else:
                # Single upper subtitle given two lower subtitles
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long upper split into two lower
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably upper repeated with different lower
                synced_list += [next]
        elif last["lower text"] == next["lower text"]:
            if isinstance(last["upper text"], float) and np.isnan(
                    last["upper text"]):
                # Lower started before upper
                last["upper text"] = next["upper text"]
                last["end"] = next["end"]
            elif isinstance(next["upper text"], float) and np.isnan(
                    next["upper text"]):
                # Upper started before lower
                if last.end < next["start"]:
                    synced_list += [next]
                else:
                    last["end"] = next["end"]
            else:
                gap = next["start"] - last["end"]
                if gap < 500:
                    # Probably long lower split into two upper
                    last["end"] = next["start"] = last["end"] + (gap / 2)
                # Otherwise, probably lower repeated with different upper
                synced_list += [next]
        else:
            synced_list += [next]
    synced_df = pd.DataFrame(synced_list)
