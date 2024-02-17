#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to hanzi text."""
from __future__ import annotations

import re

from hanziconv import HanziConv

re_hanzi = re.compile(r"[\u4e00-\u9fff]")
re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")


def get_hanzi_simplified(text: str) -> str:
    """Get the simplified version of a string containing traditional hanzi.

    Arguments:
        text: text for which to get simplified hanzi

    Returns:
        simplified text
    """
    simplified = ""

    for char in text:
        if re_hanzi.match(char) or re_hanzi_rare.match(char):
            simplified += HanziConv.toSimplified(char)
        else:
            simplified += char

    return simplified


def get_hanzi_single_line_text(text: str) -> str:
    """Merge multi-line text on a single line.

    Accounts for dashes ('﹣') used for dialogue from multiple sources.

    # TODO: Consider replacing two western spaces with one eastern space

    Arguments:
        text: text to merge
    Returns:
        merged text
    """
    # Revert strange substitution in pysubs2/subrip.py:66
    single_line = re.sub(r"\\N", r"\n", text)

    # Merge lines
    single_line = re.sub(r"^(.+)\n(.+)$", r"\1　\2", single_line, re.M)

    # Merge conversations
    conversation = re.match(
        r"^[-﹣]?\s*(?P<first>.+)[\s]+[-﹣]\s*(?P<second>.+)$", single_line
    )
    if conversation is not None:
        single_line = (
            f"﹣{conversation['first'].strip()}　　﹣{conversation['second'].strip()}"
        )

    return single_line
