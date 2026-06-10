#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core language tag handling."""

from __future__ import annotations

from scinoephile.common.described_enum import DescribedEnum

from .text import ChineseScript

__all__ = [
    "Language",
    "is_chinese_language_tag",
    "normalize_language_tag",
]

_CHINESE_LANGUAGE_CODES = {"chi", "zho", "yue"}
"""Language codes treated as Chinese."""


def is_chinese_language_tag(language: Language | str | None) -> bool:
    """Return whether a language tag should be treated as Chinese.

    Arguments:
        language: language tag, if available
    Returns:
        whether the language tag is Chinese
    """
    if language is None:
        return False
    return str(language).split("-", 1)[0].lower() in _CHINESE_LANGUAGE_CODES


def normalize_language_tag(language: str) -> str:
    """Normalize a loose language tag.

    Arguments:
        language: language tag
    Returns:
        normalized language tag
    Raises:
        ValueError: if language is empty
    """
    language = language.strip()
    if not language:
        raise ValueError("language tag may not be empty")

    parts = language.split("-")
    normalized_parts = [parts[0].lower()]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            normalized_parts.append(part.title())
        elif len(part) == 2 and part.isalpha():
            normalized_parts.append(part.upper())
        elif part.lower() == "unknown":
            normalized_parts.append("Unknown")
        else:
            normalized_parts.append(part)
    return "-".join(normalized_parts)


class Language(DescribedEnum):
    """Languages explicitly supported by Scinoephile workflows."""

    eng = ("eng", "English.")
    """English."""
    zho_hans = ("zho-Hans", "Simplified Chinese.")
    """Simplified Chinese."""
    zho_hant = ("zho-Hant", "Traditional Chinese.")
    """Traditional Chinese."""

    @property
    def is_chinese(self) -> bool:
        """Whether this language represents Chinese text."""
        return self is Language.zho_hans or self is Language.zho_hant

    @property
    def script(self) -> ChineseScript | None:
        """Chinese script implied by this language, if any."""
        if self is Language.zho_hans:
            return "simplified"
        if self is Language.zho_hant:
            return "traditional"
        return None

    @property
    def tag(self) -> str:
        """Language tag."""
        return self.value
