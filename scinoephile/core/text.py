#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to text."""
from __future__ import annotations

import re

import unicodedata

from scinoephile.core.exceptions import ScinoephileException

# See https://en.wikipedia.org/wiki/Halfwidth_and_Fullwidth_Forms_(Unicode_block)
# See https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation
half_punc = {
    "APOSTROPHE": "'",
    "BULLET": "•",
    "BULLET OPERATOR": "∙",
    "COLON": ":",
    "COMMA": ",",
    "DOT OPERATOR": "⋅",
    "DOUBLE VERTICAL LINE": "‖",
    "EM DASH": "—",
    "EN DASH": "–",
    "EXCLAMATION MARK": "!",
    "FULL STOP": ".",
    "GRAVE ACCENT": "`",
    "GREATER-THAN SIGN": ">",
    "HALFWIDTH BLACK SQUARE": "￭",
    "HALFWIDTH IDEOGRAPHIC COMMA": "､",
    "HALFWIDTH IDEOGRAPHIC FULL STOP": "｡",
    "HALFWIDTH KATAKANA MIDDLE DOT": "･",
    "HALFWIDTH LEFT CORNER BRACKET": "｢",
    "HALFWIDTH RIGHT CORNER BRACKET": "｣",
    "HALFWIDTH WHITE CIRCLE": "￮",
    "HORIZONTAL ELLIPSIS": "…",
    "HYPHEN": "‐",
    "HYPHEN-MINUS": "-",
    "LEFT CURLY BRACKET": "{",
    "LEFT DOUBLE QUOTATION MARK": "“",
    "LEFT PARENTHESIS": "(",
    "LEFT SINGLE QUOTATION MARK": "‘",
    "LEFT SQUARE BRACKET": "[",
    "LESS-THAN SIGN": "<",
    "MIDDLE DOT": "·",
    "NUMBER SIGN": "#",
    "QUESTION MARK": "?",
    "QUOTATION MARK": '"',
    "RIGHT CURLY BRACKET": "}",
    "RIGHT DOUBLE QUOTATION MARK": "”",
    "RIGHT PARENTHESIS": ")",
    "RIGHT SINGLE QUOTATION MARK": "’",
    "RIGHT SQUARE BRACKET": "]",
    "RING OPERATOR": "∘",
    "SEMICOLON": ";",
    "TILDE": "~",
}
"""Selected half-width punctuation characters."""

full_punc = {
    "DOUBLE PRIME QUOTATION MARK": "〞",
    "FULLWIDTH APOSTROPHE": "＇",
    "FULLWIDTH COLON": "：",
    "FULLWIDTH COMMA": "，",
    "FULLWIDTH EXCLAMATION MARK": "！",
    "FULLWIDTH FULL STOP": "．",
    "FULLWIDTH GRAVE ACCENT": "｀",
    "FULLWIDTH HYPHEN-MINUS": "－",
    "FULLWIDTH LEFT CURLY BRACKET": "｛",
    "FULLWIDTH LEFT PARENTHESIS": "（",
    "FULLWIDTH LEFT SQUARE BRACKET": "［",
    "FULLWIDTH LEFT WHITE PARENTHESIS": "｟",
    "FULLWIDTH NUMBER SIGN": "＃",
    "FULLWIDTH QUESTION MARK": "？",
    "FULLWIDTH QUOTATION MARK": "＂",
    "FULLWIDTH RIGHT CURLY BRACKET": "｝",
    "FULLWIDTH RIGHT PARENTHESIS": "）",
    "FULLWIDTH RIGHT SQUARE BRACKET": "］",
    "FULLWIDTH RIGHT WHITE PARENTHESIS": "｠",
    "FULLWIDTH SEMICOLON": "；",
    "FULLWIDTH TILDE": "～",
    "IDEOGRAPHIC COMMA": "、",
    "IDEOGRAPHIC FULL STOP": "。",
    "LEFT ANGLE BRACKET": "〈",
    "LEFT BLACK LENTICULAR BRACKET": "【",
    "LEFT CORNER BRACKET": "「",
    "LEFT DOUBLE ANGLE BRACKET": "《",
    "LEFT WHITE CORNER BRACKET": "『",
    "MIDLINE HORIZONTAL ELLIPSIS": "⋯",
    "REVERSED DOUBLE PRIME QUOTATION MARK": "〝",
    "RIGHT ANGLE BRACKET": "〉",
    "RIGHT BLACK LENTICULAR BRACKET": "】",
    "RIGHT CORNER BRACKET": "」",
    "RIGHT DOUBLE ANGLE BRACKET": "》",
    "RIGHT WHITE CORNER BRACKET": "』",
}
"""Selected full-width punctuation characters."""

half_to_full_punc = {
    **{
        half_punc[key]: full_punc[f"FULLWIDTH {key}"]
        for key in half_punc
        if f"FULLWIDTH {key}" in full_punc
    },
    "“": "〝",
    "”": "〞",
}
"""Mapping from half-width to full-width punctuation characters."""

full_to_half_punc = {v: k for k, v in half_to_full_punc.items()}
"""Mapping from full-width to half-width punctuation characters."""

re_hanzi = re.compile(r"[\u4e00-\u9fff]")
"""Regular expression for Hanzi characters."""

re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")
"""Regular expression for rare Hanzi characters."""

re_western = re.compile(r"[a-zA-Z0-9]")
"""Regular expression for Western characters."""


def get_char_type(char: str) -> str:
    """Return character type.

    Arguments:
        char: Character
    Returns:
        Character type
    Raises:
        ScinoephileException: If character type is not recognized
    """
    punctuation = set(half_punc.values()) | set(full_punc.values())

    # Check if character is punctuation
    if char in punctuation:
        return "punc"

    # Check if character is full-width (CJK)
    if any(
        [
            "\u4E00" <= char <= "\u9FFF",  # CJK Unified Ideographs
            "\u3400" <= char <= "\u4DBF",  # CJK Unified Ideographs Extension A
            "\uF900" <= char <= "\uFAFF",  # CJK Compatibility Ideographs
            "\U00020000" <= char <= "\U0002A6DF",  # CJK Unified Ideographs Ext B
            "\U0002A700" <= char <= "\U0002B73F",  # CJK Unified Ideographs Ext C
            "\U0002B740" <= char <= "\U0002B81F",  # CJK Unified Ideographs Ext D
            "\U0002B820" <= char <= "\U0002CEAF",  # CJK Unified Ideographs Ext E
            "\U0002CEB0" <= char <= "\U0002EBEF",  # CJK Unified Ideographs Ext F
            "\u3000" <= char <= "\u303F",  # CJK Symbols and Punctuation
        ]
    ):
        return "full"

    # Check if character is half-width (Western)
    if any(
        [
            "\u0020" <= char <= "\u007F",  # Basic Latin
            "\u00A0" <= char <= "\u00FF",  # Latin-1 Supplement
            "\u0100" <= char <= "\u017F",  # Latin Extended-A
            "\u0180" <= char <= "\u024F",  # Latin Extended-B
        ]
    ):
        return "half"

    # Raise exception if character type is not recognized
    raise ScinoephileException(
        f"Unrecognized char type for '{char}' of name {unicodedata.name(char)}"
    )


def get_text_type(text: str) -> str:
    """Determine whether a string contains Chinese characters.

    Arguments:
        text: Text to analyze
    Returns:
        Whether the text contains Chinese characters
    """
    for char in text:
        if get_char_type(char) == "full":
            return "full"
        return "half"
