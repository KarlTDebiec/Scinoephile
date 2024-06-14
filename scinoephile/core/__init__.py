#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code for scinoephile.

Code within this module may import only from scinoephile.common.

Most functions herein follow the naming convention:
    get_(english|hanzi|cantonese_pinyin|mandarin_pinyin)_(character|text|subtitles)_(description)
"""
from __future__ import annotations

from scinoephile.core.cantonese import (
    get_cantonese_pinyin_character,
    get_cantonese_pinyin_subtitles,
    get_cantonese_pinyin_text,
)
from scinoephile.core.english import (
    get_english_subtitles_merged_to_single_line,
    get_english_subtitles_truecased,
    get_english_text_merged_to_single_line,
    get_english_text_truecased,
)
from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.hanzi import (
    get_hanzi_subtitles_merged_to_single_line,
    get_hanzi_subtitles_simplified,
    get_hanzi_text_merged_to_single_line,
    get_hanzi_text_simplified,
)
from scinoephile.core.mandarin import (
    get_mandarin_pinyin_subtitles,
    get_mandarin_pinyin_text,
)
from scinoephile.core.subtitle import Subtitle
from scinoephile.core.subtitle_series import SubtitleSeries
from scinoephile.core.subtitles import (
    get_subtitle_blocks_for_synchronization,
    get_subtitles_block_by_index,
    get_subtitles_block_by_time,
)

__all__ = [
    "ScinoephileException",
    "Subtitle",
    "SubtitleSeries",
    "get_subtitle_blocks_for_synchronization",
    "get_subtitles_block_by_index",
    "get_subtitles_block_by_time",
    "get_cantonese_pinyin_character",
    "get_cantonese_pinyin_subtitles",
    "get_cantonese_pinyin_text",
    "get_english_subtitles_merged_to_single_line",
    "get_english_subtitles_truecased",
    "get_english_text_merged_to_single_line",
    "get_english_text_truecased",
    "get_hanzi_subtitles_merged_to_single_line",
    "get_hanzi_subtitles_simplified",
    "get_hanzi_text_merged_to_single_line",
    "get_hanzi_text_simplified",
    "get_mandarin_pinyin_subtitles",
    "get_mandarin_pinyin_text",
]
