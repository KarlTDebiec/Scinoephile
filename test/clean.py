#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from scinoephile.core import Series
from scinoephile.core.english import get_english_merged
from scinoephile.core.hanzi import get_hanzi_series_merged_to_single_line

english = Series.load(r"C:\Users\karls\Code\Scinoephile\test\data\mnt\input\en-US.srt")
english = get_english_merged(english)
english.save("en-US.srt")

hanzi = Series.load(r"C:\Users\karls\Code\Scinoephile\test\data\mnt\input\cmn-Hans.srt")
hanzi = get_hanzi_series_merged_to_single_line(hanzi)
hanzi.save("cmn-Hans.srt")
