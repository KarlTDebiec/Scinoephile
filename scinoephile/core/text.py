#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to text."""

from __future__ import annotations

import re
import unicodedata
from enum import Enum
from functools import cache
from textwrap import dedent
from typing import Literal

from .exceptions import ScinoephileError

__all__ = [
    "ChineseScript",
    "HALF_PUNC",
    "FULL_PUNC",
    "WHITESPACE",
    "HALF_PUNC_CHARS",
    "FULL_PUNC_CHARS",
    "WHITESPACE_CHARS",
    "HALF_TO_FULL_PUNC",
    "FULL_TO_HALF_PUNC",
    "RE_ASS_OVERRIDE_BLOCK",
    "RE_HANZI",
    "RE_LATIN_WORD",
    "RE_PRIVATE_USE_AREA_BMP",
    "RE_WESTERN",
    "RE_WHITESPACE",
    "AnsiColor",
    "colorize",
    "dedent_and_compact",
    "get_char_type",
    "is_full_width_char",
    "normalize_fullwidth_alphanumerics",
    "normalize_ocr_confusables",
    "normalize_text",
    "replace_control_characters",
    "remove_non_punc_and_whitespace",
    "remove_punc_and_whitespace",
]


type ChineseScript = Literal["simplified", "traditional"]
"""Chinese script supported by text processing helpers."""


class AnsiColor(Enum):
    """ANSI escape codes for terminal text coloring."""

    RESET = "\x1b[0m"
    """Reset terminal text styling."""
    GREEN = "\x1b[32m"
    """Green terminal text."""
    RED = "\x1b[31m"
    """Red terminal text."""
    BLUE = "\x1b[34m"
    """Blue terminal text."""
    PURPLE = "\x1b[35m"
    """Purple terminal text."""


# See https://en.wikipedia.org/wiki/Halfwidth_and_Fullwidth_Forms_(Unicode_block)
# See https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation
HALF_PUNC = {
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

FULL_PUNC = {
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

WHITESPACE = {
    "IDEOGRAPHIC SPACE": "　",
    "SPACE": " ",
}
"""Selected whitespace characters."""

HALF_PUNC_CHARS = set(HALF_PUNC.values())
"""Set of half-width punctuation characters."""

FULL_PUNC_CHARS = set(FULL_PUNC.values())
"""Set of full-width punctuation characters."""

WHITESPACE_CHARS = set(WHITESPACE.values())
"""Set of whitespace characters."""

HALF_TO_FULL_PUNC = {
    **{
        HALF_PUNC[key]: FULL_PUNC[f"FULLWIDTH {key}"]
        for key in HALF_PUNC
        if f"FULLWIDTH {key}" in FULL_PUNC
    },
    **{
        HALF_PUNC[f"HALFWIDTH {key}"]: FULL_PUNC[key]
        for key in FULL_PUNC
        if f"HALFWIDTH {key}" in HALF_PUNC
    },
    "“": "〝",
    "”": "〞",
    "…": "⋯",
}
"""Mapping from half-width to full-width punctuation characters."""

FULL_TO_HALF_PUNC = {v: k for k, v in HALF_TO_FULL_PUNC.items()}
"""Mapping from full-width to half-width punctuation characters."""

_FULLWIDTH_ALPHANUMERICS_TO_ASCII = str.maketrans(
    {
        **{chr(code): chr(code - 0xFEE0) for code in range(0xFF10, 0xFF1A)},
        **{chr(code): chr(code - 0xFEE0) for code in range(0xFF21, 0xFF3B)},
        **{chr(code): chr(code - 0xFEE0) for code in range(0xFF41, 0xFF5B)},
    }
)
"""Mapping from fullwidth ASCII letters and digits to regular ASCII."""

_OCR_CONFUSABLES_TO_ASCII = str.maketrans(
    {
        "Κ": "K",
        "Ο": "O",
        "κ": "k",
        "ο": "o",
    }
)
"""Mapping from OCR-confusable characters to regular ASCII."""

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

RE_ASS_OVERRIDE_BLOCK = re.compile(r"\{[^{}]*\}")
"""Regular expression for ASS override blocks."""

RE_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z']*")
"""Regular expression for Latin words."""

RE_PRIVATE_USE_AREA_BMP = re.compile(r"[\ue000-\uf8ff]")
"""Regular expression for BMP private-use area code points."""

RE_WESTERN = re.compile(r"[a-zA-Z0-9]")
"""Regular expression for Western characters."""

RE_WHITESPACE = re.compile(r"\s+")
"""Regular expression for runs of whitespace."""


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


def colorize(text: str, color: AnsiColor) -> str:
    """Colorize text with an ANSI escape.

    Arguments:
        text: input text
        color: ANSI color escape
    Returns:
        colorized text
    """
    return f"{color.value}{text}{AnsiColor.RESET.value}"


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
    punctuation = set(HALF_PUNC.values()) | set(FULL_PUNC.values())

    # Check if character is punctuation
    if char in punctuation:
        return "punc"

    # Reject control, format, and combining characters unsupported by this model
    if unicodedata.category(char).startswith(("C", "M")):
        name = unicodedata.name(char, "<unnamed>")
        raise ScinoephileError(f"Unrecognized char type for {char!r} of name {name}")

    # Check Unicode characters with wide or full-width display properties
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return "full"

    # Treat narrow, half-width, neutral, and ambiguous characters as half-width
    return "half"


def is_full_width_char(char: str) -> bool:
    """Return whether a character should occupy a full-width display column.

    Arguments:
        char: character to classify
    Returns:
        whether the character should use full-width spacing
    """
    if char in FULL_PUNC_CHARS:
        return True
    return get_char_type(char) == "full"


def normalize_fullwidth_alphanumerics(text: str) -> str:
    """Convert fullwidth ASCII letters and digits to regular ASCII.

    Arguments:
        text: text to normalize
    Returns:
        text with fullwidth alphanumeric characters normalized
    """
    return text.translate(_FULLWIDTH_ALPHANUMERICS_TO_ASCII)


def normalize_ocr_confusables(text: str) -> str:
    """Convert OCR-confusable characters to regular ASCII.

    Arguments:
        text: text to normalize
    Returns:
        text with OCR-confusable characters normalized
    """
    return text.translate(_OCR_CONFUSABLES_TO_ASCII)


def normalize_text(text: str) -> str:
    """Normalize text using non-language-specific cleanup.

    Arguments:
        text: text to normalize
    Returns:
        normalized text
    """
    normalized = replace_control_characters(text)
    normalized = normalized.replace("\xa0", " ").strip()
    normalized = normalize_fullwidth_alphanumerics(normalized)
    return normalize_ocr_confusables(normalized)


def remove_non_punc_and_whitespace(text: str) -> str:
    """Strip non-punctuation and non-whitespace characters from text.

    Arguments:
        text: Text to strip
    Returns:
        Stripped text with only punctuation and whitespace remaining
    """
    chars_to_keep = HALF_PUNC_CHARS | FULL_PUNC_CHARS | WHITESPACE_CHARS
    return "".join(char for char in text if char.isspace() or char in chars_to_keep)


def remove_punc_and_whitespace(text: str) -> str:
    """Strip punctuation and whitespace from text.

    Arguments:
        text: Text to strip
    Returns:
        Stripped text with punctuation and whitespace removed
    """
    chars_to_remove = HALF_PUNC_CHARS | FULL_PUNC_CHARS | WHITESPACE_CHARS
    return "".join(
        char for char in text if not char.isspace() and char not in chars_to_remove
    )


def replace_control_characters(text: str) -> str:
    """Replace invalid control characters in text.

    Arguments:
        text: text to process
    Returns:
        text with unsupported control characters replaced by spaces
    """
    return "".join(
        char if unicodedata.category(char)[0] != "C" or char in "\t\n\r" else " "
        for char in text
    )
