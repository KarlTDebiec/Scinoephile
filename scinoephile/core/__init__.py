#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code."""
from __future__ import annotations

from scinoephile.core.cantonese import (
    get_cantonese_pinyin,
    get_cantonese_pinyin_for_single_hanzi,
)
from scinoephile.core.english import get_english_single_line_text, get_english_truecase
from scinoephile.core.exception import ScinoephileException
from scinoephile.core.hanzi import get_hanzi_simplified, get_hanzi_single_line_text
from scinoephile.core.mandarin import get_mandarin_pinyin
from scinoephile.core.subtitle import Subtitle
from scinoephile.core.subtitle_series import SubtitleSeries

__all__ = [
    "ScinoephileException",
    "Subtitle",
    "SubtitleSeries",
    "get_cantonese_pinyin",
    "get_cantonese_pinyin_for_single_hanzi",
    "get_english_single_line_text",
    "get_english_truecase",
    "get_hanzi_simplified",
    "get_hanzi_single_line_text",
    "get_mandarin_pinyin",
]
