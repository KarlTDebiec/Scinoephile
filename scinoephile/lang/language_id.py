#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language identification results for Chinese scripts and romanizations."""

from __future__ import annotations

from dataclasses import dataclass

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

    @classmethod
    def from_text(cls, text: str) -> LanguageId:
        """Build language identification results from text.

        Arguments:
            text: input text to classify
        Returns:
            language identification results
        """
        return cls(
            text=text,
            is_accented_pinyin=is_accented_pinyin_fn(text),
            is_numbered_pinyin=is_numbered_pinyin_fn(text),
            is_accented_yale=is_accented_yale_fn(text),
            is_numbered_jyutping=is_numbered_jyutping_fn(text),
            is_simplified=is_simplified_fn(text),
            is_traditional=is_traditional_fn(text),
        )
