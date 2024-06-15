#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from scinoephile.core import (
    SubtitleSeries,
    get_english_subtitles_merged_to_single_line,
    get_hanzi_subtitles_merged_to_single_line,
)

english = SubtitleSeries.load(
    r"C:\Users\karls\Code\Scinoephile\test\data\mnt\input\en-US.srt"
)
english = get_english_subtitles_merged_to_single_line(english)
english.save("en-US.srt")

hanzi = SubtitleSeries.load(
    r"C:\Users\karls\Code\Scinoephile\test\data\mnt\input\cmn-Hans.srt"
)
hanzi = get_hanzi_subtitles_merged_to_single_line(hanzi)
hanzi.save("cmn-Hans.srt")
