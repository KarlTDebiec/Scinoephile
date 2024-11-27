#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""
from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_merged
from scinoephile.core.hanzi import get_hanzi_merged, get_hanzi_simplified
from scinoephile.core.synchronization import get_synced_series
from scinoephile.testing.file import get_test_file_path

if __name__ == "__main__":

    def get_output_path(relative_path: str) -> Path:
        return package_root.parent / "test" / "data" / Path(relative_path)

    # English
    en_hk = Series.load(get_test_file_path("kob/input/en-HK.srt"))
    en_hk_clean = get_english_cleaned(en_hk)
    en_hk_clean.save(get_output_path("kob/output/en-HK_clean.srt"))
    en_hk_merge = get_english_merged(en_hk)
    en_hk_merge.save(get_output_path("kob/output/en-HK_merge.srt"))

    # Simplified Cantonese Chinese
    yue_hans_hk = Series.load(get_test_file_path("kob/input/yue-Hans-HK.srt"))
    yue_hans_hk_merge = get_hanzi_merged(yue_hans_hk)
    yue_hans_hk_merge.save(get_output_path("kob/output/yue-Hans-HK_merge.srt"))

    # Traditional Cantonese Chinese
    yue_hant_hk = Series.load(get_test_file_path("kob/input/yue-Hant-HK.srt"))
    yue_hant_hk_simplify = get_hanzi_simplified(yue_hant_hk)
    yue_hant_hk_simplify.save(get_output_path("kob/output/yue-Hant-HK_simplify.srt"))

    # Bilingual Simplified Cantonese Chinese and English
    en_hk_clean_merge = get_english_merged(en_hk_clean)
    yue_hans_hk_en_hk = get_synced_series(yue_hans_hk_merge, en_hk_clean_merge)
    yue_hans_hk_en_hk.save(get_output_path("kob/output/yue-Hans-HK_en-HK.srt"))
