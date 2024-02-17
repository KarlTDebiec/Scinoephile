#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import re
from typing import List

punctuation = {
    "\n": "\n",
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
    "“": '"',
    "”": '"',
    '"': '"',
    "《": "<",
    "》": ">",
    "「": "[",
    "」": "]",
    "：": ":",
}
re_hanzi = re.compile(r"[\u4e00-\u9fff]")
re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")
re_western = re.compile(r"[a-zA-Z0-9]")


def get_list_for_display(
        list_of_strings: List[str], linker: str = "and", quote: str = "'"
) -> str:
    # TODO: Document
    string = quote + f"{quote}, {quote}".join(list_of_strings) + quote
    if len(list_of_strings) == 2:
        string = re.sub(r"(.*), ", rf"\1 {linker} ", string)
    elif len(list_of_strings) > 2:
        string = re.sub(r"(.*), ", rf"\1, {linker} ", string)
    return string


def get_simplified_hanzi(text: str, verbosity: int = 1) -> str:
    """
    Converts traditional hanzi to simplified.

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


def get_pinyin(text: str, language: str = "mandarin", verbosity: int = 1) -> str:
    """
    Converts hanzi to pinyin.

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
                            [a[0] for a in pinyin(word)]
                        )
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
        raise ValueError(
            "Invalid value provided for 'language'; must be 'cantonese' or 'mandarin'"
        )
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
        single_line = re.sub(
            r"^\s*-\s*(.+)\n-\s*(.+)\s*$", r"- \1    - \2", single_line, re.M
        )
        single_line = re.sub(r"^\s*(.+)\s*\n\s*(.+)\s*$", r"\1 \2", single_line, re.M)
    elif language == "hanzi":
        print(text)
        single_line = re.sub(r"^(.+)\n(.+)$", r"\1　\2", single_line, re.M)
        print(single_line)
        conversation = re.match(
            r"^[-﹣]?\s*(?P<first>.+)[\s]+[-﹣]\s*(?P<second>.+)$", single_line
        )
        if conversation is not None:
            single_line = f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        print(single_line)
    else:
        raise ValueError(
            "Invalid value for argument 'language'; must be "
            "'english', 'hanzi', or 'pinyin'"
        )

    return single_line
