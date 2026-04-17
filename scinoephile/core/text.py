#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to text."""

from __future__ import annotations

import re
import unicodedata
from functools import cache
from textwrap import dedent

from .exceptions import ScinoephileError

__all__ = [
    "half_punc",
    "full_punc",
    "whitespace",
    "half_punc_chars",
    "full_punc_chars",
    "whitespace_chars",
    "half_to_full_punc",
    "full_to_half_punc",
    "RE_HANZI",
    "RE_PRIVATE_USE_AREA_BMP",
    "RE_WESTERN",
    "dedent_and_compact",
    "get_char_type",
    "remove_non_punc_and_whitespace",
    "remove_punc_and_whitespace",
]

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
    "EIGHTH NOTE": "♪",
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
    "SOLIDUS": "/",
    "TILDE": "~",
}
"""Selected half-width punctuation characters."""

full_punc = {
    "BOX DRAWINGS LIGHT HORIZONTAL": "─",
    "DOUBLE PRIME QUOTATION MARK": "〞",
    "FULLWIDTH APOSTROPHE": "＇",
    "FULLWIDTH COLON": "：",
    "FULLWIDTH COMMA": "，",
    "FULLWIDTH EXCLAMATION MARK": "！",
    "FULLWIDTH FULL STOP": "．",
    "FULLWIDTH GRAVE ACCENT": "｀",
    "FULLWIDTH GREATER-THAN SIGN": "＞",
    "FULLWIDTH HYPHEN-MINUS": "－",
    "FULLWIDTH LEFT CURLY BRACKET": "｛",
    "FULLWIDTH LEFT PARENTHESIS": "（",
    "FULLWIDTH LEFT SQUARE BRACKET": "［",
    "FULLWIDTH LEFT WHITE PARENTHESIS": "｟",
    "FULLWIDTH LESS-THAN SIGN": "＜",
    "FULLWIDTH NUMBER SIGN": "＃",
    "FULLWIDTH QUESTION MARK": "？",
    "FULLWIDTH QUOTATION MARK": "＂",
    "FULLWIDTH RIGHT CURLY BRACKET": "｝",
    "FULLWIDTH RIGHT PARENTHESIS": "）",
    "FULLWIDTH RIGHT SQUARE BRACKET": "］",
    "FULLWIDTH RIGHT WHITE PARENTHESIS": "｠",
    "FULLWIDTH SEMICOLON": "；",
    "FULLWIDTH SOLIDUS": "／",
    "FULLWIDTH TILDE": "～",
    "IDEOGRAPHIC COMMA": "、",
    "IDEOGRAPHIC FULL STOP": "。",
    "KATAKANA MIDDLE DOT": "・",
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
    "SMALL HYPHEN-MINUS": "﹣",
}
"""Selected full-width punctuation characters."""

whitespace = {
    "IDEOGRAPHIC SPACE": "　",
    "SPACE": " ",
}
"""Selected whitespace characters."""

half_punc_chars = set(half_punc.values())
"""Set of half-width punctuation characters."""

full_punc_chars = set(full_punc.values())
"""Set of full-width punctuation characters."""

whitespace_chars = set(whitespace.values())
"""Set of whitespace characters."""

half_to_full_punc = {
    **{
        half_punc[key]: full_punc[f"FULLWIDTH {key}"]
        for key in half_punc
        if f"FULLWIDTH {key}" in full_punc
    },
    "“": "〝",
    "”": "〞",
    "·": "・",
}
"""Mapping from half-width to full-width punctuation characters."""

full_to_half_punc = {v: k for k, v in half_to_full_punc.items()}
"""Mapping from full-width to half-width punctuation characters."""

RE_HANZI = re.compile(
    r"[\u4e00-\u9fff"
    r"\u3400-\u4DBF"
    r"\U00020000-\U0002A6DF"
    r"\U0002A700-\U0002B73F"
    r"\U0002B740-\U0002B81F"
    r"\U0002B820-\U0002CEAF"
    r"\U0002CEB0-\U0002EBEF"
    r"\U0002EBF0-\U0002EE5D"
    r"\U00030000-\U0003134A"
    r"\U00031350-\U000323AF]"
)
"""Regular expression for Hanzi characters.

Includes the following Unicode blocks:
  - CJK Unified Ideographs (U+4E00–U+9FFF)
  - CJK Unified Ideographs Extension A (U+3400–U+4DBF)
  - CJK Unified Ideographs Extension B (U+20000–U+2A6DF)
  - CJK Unified Ideographs Extension C (U+2A700–U+2B73F)
  - CJK Unified Ideographs Extension D (U+2B740–U+2B81F)
  - CJK Unified Ideographs Extension E (U+2B820–U+2CEAF)
  - CJK Unified Ideographs Extension F (U+2CEB0–U+2EBEF)
  - CJK Unified Ideographs Extension I (U+2EBF0–U+2EE5D)
  - CJK Unified Ideographs Extension G (U+30000–U+3134A)
  - CJK Unified Ideographs Extension H (U+31350–U+323AF)
"""

RE_PRIVATE_USE_AREA_BMP = re.compile(r"[\ue000-\uf8ff]")
"""Regular expression for BMP private-use area code points."""

RE_WESTERN = re.compile(r"[a-zA-Z0-9]")
"""Regular expression for Western characters."""


def dedent_and_compact(text: str) -> str:
    """Get multi-line string dedented and with newlines compacted.

    Arguments:
        text: text to process
    Returns:
        dedented and compacted text
    """
    text = dedent(text).strip()
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


@cache
def get_char_type(char: str) -> str:
    """Return character type.

    Arguments:
        char: Character
    Returns:
        Character type
    Raises:
        ScinoephileError: If character type is not recognized
    """
    punctuation = set(half_punc.values()) | set(full_punc.values())

    # Check if character is punctuation
    if char in punctuation:
        return "punc"

    # Check if character is full-width (CJK)
    if any(
        [
            "\u4e00" <= char <= "\u9fff",  # CJK Unified Ideographs
            "\u3400" <= char <= "\u4dbf",  # CJK Unified Ideographs Extension A
            "\uf900" <= char <= "\ufaff",  # CJK Compatibility Ideographs
            "\U00020000" <= char <= "\U0002a6df",  # CJK Unified Ideographs Ext B
            "\U0002a700" <= char <= "\U0002b73f",  # CJK Unified Ideographs Ext C
            "\U0002b740" <= char <= "\U0002b81f",  # CJK Unified Ideographs Ext D
            "\U0002b820" <= char <= "\U0002ceaf",  # CJK Unified Ideographs Ext E
            "\U0002ceb0" <= char <= "\U0002ebef",  # CJK Unified Ideographs Ext F
            "\U0002ebf0" <= char <= "\U0002ee5d",  # CJK Unified Ideographs Ext I
            "\U00030000" <= char <= "\U0003134a",  # CJK Unified Ideographs Ext G
            "\U00031350" <= char <= "\U000323af",  # CJK Unified Ideographs Ext H
            "\u3000" <= char <= "\u303f",  # CJK Symbols and Punctuation
        ]
    ):
        return "full"

    # Check if character is half-width (Western)
    if any(
        [
            "\u0020" <= char <= "\u007f",  # Basic Latin
            "\u00a0" <= char <= "\u00ff",  # Latin-1 Supplement
            "\u0100" <= char <= "\u017f",  # Latin Extended-A
            "\u0180" <= char <= "\u024f",  # Latin Extended-B
        ]
    ):
        return "half"

    # Raise exception if character type is not recognized
    raise ScinoephileError(
        f"Unrecognized char type for '{char}' of name {unicodedata.name(char)}"
    )


def remove_non_punc_and_whitespace(text: str) -> str:
    """Strip non-punctuation and non-whitespace characters from text.

    Arguments:
        text: Text to strip
    Returns:
        Stripped text with only punctuation and whitespace remaining
    """
    chars_to_remove = set(text) - (half_punc_chars | full_punc_chars | whitespace_chars)
    return re.sub(f"[{re.escape(''.join(chars_to_remove))}]", "", text)


def remove_punc_and_whitespace(text: str) -> str:
    """Strip punctuation and whitespace from text.

    Arguments:
        text: Text to strip
    Returns:
        Stripped text with punctuation and whitespace removed
    """
    chars_to_remove = half_punc_chars | full_punc_chars | whitespace_chars
    return "".join(
        char for char in text if not char.isspace() and char not in chars_to_remove
    )
