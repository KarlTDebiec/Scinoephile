#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to text."""
from __future__ import annotations

import re

# See https://en.wikipedia.org/wiki/Halfwidth_and_Fullwidth_Forms_(Unicode_block)
# See https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation
half_punc_dict = {
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

full_punc_dict = {
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
