#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language identification results for text inputs."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core import Language
from scinoephile.core.text import (
    RE_ASS_OVERRIDE_BLOCK,
    RE_HANZI,
    RE_LATIN_WORD,
    RE_WHITESPACE,
    normalize_text,
)
from scinoephile.lang.cmn.romanization import (
    is_accented_pinyin as is_accented_pinyin_fn,
)
from scinoephile.lang.cmn.romanization import (
    is_numbered_pinyin as is_numbered_pinyin_fn,
)
from scinoephile.lang.yue.romanization import is_accented_yale as is_accented_yale_fn
from scinoephile.lang.yue.romanization import (
    is_numbered_jyutping as is_numbered_jyutping_fn,
)
from scinoephile.lang.zho.script.analysis import is_simplified as is_simplified_fn
from scinoephile.lang.zho.script.analysis import is_traditional as is_traditional_fn

__all__ = ["LanguageId"]

MIN_ENGLISH_WORDS = 2
"""Minimum number of English-looking words needed for text classification."""
MIN_ENGLISH_WORD_LENGTH = 4
"""Minimum English-looking word length needed for short text classification."""
CANTONESE_MARKERS = frozenset(
    {
        "佢",
        "係咪",
        "系咪",
        "俾",
        "冇",
        "咁",
        "咗",
        "咩",
        "哋",
        "呀",
        "唔",
        "啱",
        "啲",
        "啦",
        "喇",
        "喎",
        "喺",
        "嗰",
        "嘅",
        "嘢",
        "嚟",
        "㗎",
        "乜",
        "畀",
        "睇",
    }
)
"""High-signal written Cantonese markers."""
STANDARD_CHINESE_MARKERS = frozenset(
    {
        "他",
        "她",
        "它",
        "的",
        "了",
        "在",
        "是",
        "没",
        "沒",
        "这",
        "這",
        "那",
        "们",
        "們",
        "吗",
        "嗎",
    }
)
"""High-signal standard Chinese markers."""


@dataclass
class LanguageId:
    """Language identification result for a text input."""

    text: str
    """Input text to classify."""

    is_accented_pinyin: bool
    """Accented pinyin classification."""

    is_numbered_pinyin: bool
    """Numbered pinyin classification."""

    is_accented_yale: bool
    """Accented Yale classification."""

    is_numbered_jyutping: bool
    """Numbered Jyutping classification."""

    is_simplified: bool
    """Simplified Chinese classification."""

    is_traditional: bool
    """Traditional Chinese classification."""

    language: Language | None = None
    """Detected language, when the text has enough signal."""

    @classmethod
    def from_text(cls, text: str) -> LanguageId:
        """Build language identification results from text.

        Arguments:
            text: input text to classify
        Returns:
            language identification results
        """
        normalized_text = normalize_text(text)
        normalized_text = normalized_text.replace("\\N", " ")
        normalized_text = RE_ASS_OVERRIDE_BLOCK.sub(" ", normalized_text)
        normalized_text = RE_WHITESPACE.sub(" ", normalized_text).strip()
        is_accented_pinyin = is_accented_pinyin_fn(normalized_text)
        is_numbered_pinyin = is_numbered_pinyin_fn(normalized_text)
        is_accented_yale = is_accented_yale_fn(normalized_text)
        is_numbered_jyutping = is_numbered_jyutping_fn(normalized_text)
        is_simplified = is_simplified_fn(normalized_text)
        is_traditional = is_traditional_fn(normalized_text)

        return cls(
            text=text,
            is_accented_pinyin=is_accented_pinyin,
            is_numbered_pinyin=is_numbered_pinyin,
            is_accented_yale=is_accented_yale,
            is_numbered_jyutping=is_numbered_jyutping,
            is_simplified=is_simplified,
            is_traditional=is_traditional,
            language=cls._get_language(
                normalized_text,
                is_accented_pinyin=is_accented_pinyin,
                is_numbered_pinyin=is_numbered_pinyin,
                is_accented_yale=is_accented_yale,
                is_numbered_jyutping=is_numbered_jyutping,
                is_simplified=is_simplified,
                is_traditional=is_traditional,
            ),
        )

    @staticmethod
    def _get_chinese_language(
        text: str,
        *,
        is_simplified: bool,
        is_traditional: bool,
    ) -> Language | None:
        """Get the Chinese language represented by text.

        Arguments:
            text: normalized text to classify
            is_simplified: whether the text appears to be simplified Chinese
            is_traditional: whether the text appears to be traditional Chinese
        Returns:
            detected Chinese language, if conclusive
        """
        if is_simplified and not is_traditional:
            standard_language = Language.zho_hans
            cantonese_language = Language.yue_hans
        elif is_traditional and not is_simplified:
            standard_language = Language.zho_hant
            cantonese_language = Language.yue_hant
        else:
            return None

        cantonese_count = sum(text.count(marker) for marker in CANTONESE_MARKERS)
        standard_count = sum(text.count(marker) for marker in STANDARD_CHINESE_MARKERS)
        if cantonese_count > standard_count:
            return cantonese_language

        if standard_count > cantonese_count:
            return standard_language
        return None

    @staticmethod
    def _get_language(
        text: str,
        *,
        is_accented_pinyin: bool,
        is_numbered_pinyin: bool,
        is_accented_yale: bool,
        is_numbered_jyutping: bool,
        is_simplified: bool,
        is_traditional: bool,
    ) -> Language | None:
        """Get the language represented by text.

        Arguments:
            text: normalized text to classify
            is_accented_pinyin: whether text is accented pinyin
            is_numbered_pinyin: whether text is numbered pinyin
            is_accented_yale: whether text is accented Yale romanization
            is_numbered_jyutping: whether text is numbered Jyutping
            is_simplified: whether text appears to be simplified Chinese
            is_traditional: whether text appears to be traditional Chinese
        Returns:
            detected language, if conclusive
        """
        if not text:
            return None

        has_romanization = (
            is_accented_pinyin
            or is_numbered_pinyin
            or is_accented_yale
            or is_numbered_jyutping
        )
        if has_romanization:
            return None

        if RE_HANZI.search(text) is None:
            words = RE_LATIN_WORD.findall(text)
            if len(words) >= MIN_ENGLISH_WORDS and any(
                len(word) >= MIN_ENGLISH_WORD_LENGTH for word in words
            ):
                return Language.eng
            return None

        return LanguageId._get_chinese_language(
            text,
            is_simplified=is_simplified,
            is_traditional=is_traditional,
        )
