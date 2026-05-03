#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language identification results for Chinese scripts and romanizations."""

from __future__ import annotations

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
from scinoephile.lang.zho.conversion import is_simplified as is_simplified_fn
from scinoephile.lang.zho.conversion import is_traditional as is_traditional_fn

__all__ = ["LanguageIDResult"]


class LanguageIDResult:
    """Language identification result for a text input.

    Arguments:
        text: input text to classify
        is_accented_pinyin: override accented pinyin classification
        is_numbered_pinyin: override numbered pinyin classification
        is_accented_yale: override accented Yale classification
        is_numbered_jyutping: override numbered Jyutping classification
        is_simplified: override simplified Chinese classification
        is_traditional: override traditional Chinese classification
    """

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

    def __init__(
        self,
        text: str,
        *,
        is_accented_pinyin: bool | None = None,
        is_numbered_pinyin: bool | None = None,
        is_accented_yale: bool | None = None,
        is_numbered_jyutping: bool | None = None,
        is_simplified: bool | None = None,
        is_traditional: bool | None = None,
    ):
        """Initialize language identification results.

        Arguments:
            text: input text to classify
            is_accented_pinyin: override accented pinyin classification
            is_numbered_pinyin: override numbered pinyin classification
            is_accented_yale: override accented Yale classification
            is_numbered_jyutping: override numbered Jyutping classification
            is_simplified: override simplified Chinese classification
            is_traditional: override traditional Chinese classification
        """
        self.text = text
        self.is_accented_pinyin = (
            is_accented_pinyin
            if is_accented_pinyin is not None
            else is_accented_pinyin_fn(text)
        )
        self.is_numbered_pinyin = (
            is_numbered_pinyin
            if is_numbered_pinyin is not None
            else is_numbered_pinyin_fn(text)
        )
        self.is_accented_yale = (
            is_accented_yale
            if is_accented_yale is not None
            else is_accented_yale_fn(text)
        )
        self.is_numbered_jyutping = (
            is_numbered_jyutping
            if is_numbered_jyutping is not None
            else is_numbered_jyutping_fn(text)
        )
        self.is_simplified = (
            is_simplified if is_simplified is not None else is_simplified_fn(text)
        )
        self.is_traditional = (
            is_traditional if is_traditional is not None else is_traditional_fn(text)
        )
