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
    yue_hans = ("yue-Hans", "Cantonese, simplified Chinese script.")
    """Cantonese in simplified Chinese script."""
    yue_hant = ("yue-Hant", "Cantonese, traditional Chinese script.")
    """Cantonese in traditional Chinese script."""
    zho_hans = ("zho-Hans", "Simplified Chinese.")
    """Simplified Chinese."""
    zho_hant = ("zho-Hant", "Traditional Chinese.")
    """Traditional Chinese."""

    @property
    def is_cantonese(self) -> bool:
        """Whether this language is Cantonese."""
        return self in (Language.yue_hans, Language.yue_hant)

    @property
    def is_chinese(self) -> bool:
        """Whether this language is Chinese."""
        return self in (
            Language.yue_hans,
            Language.yue_hant,
            Language.zho_hans,
            Language.zho_hant,
        )

    @property
    def language(self) -> str:
        """Language component of the complete code."""
        return self.code.partition("-")[0]

    @property
    def script(self) -> ChineseScript | None:
        """Chinese script subtag from the complete code, if any."""
        script = self.code.partition("-")[2]
        if script in ("Hans", "Hant"):
            return script
        return None
