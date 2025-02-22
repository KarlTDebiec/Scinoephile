#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to text."""
from __future__ import annotations

import re

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
"""Mapping of punctuation characters, some full-width, to single-width counterparts."""

re_hanzi = re.compile(r"[\u4e00-\u9fff]")
"""Regular expression for Hanzi characters."""

re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")
"""Regular expression for rare Hanzi characters."""

re_western = re.compile(r"[a-zA-Z0-9]")
"""Regular expression for Western characters."""


def is_chinese(text: str) -> bool:
    """Determine whether a string contains Chinese characters.

    Arguments:
        text: Text to analyze
    Returns:
        Whether the text contains Chinese characters
    """
    return bool(re_hanzi.search(text)) or bool(re_hanzi_rare.search(text))
