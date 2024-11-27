#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""
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

    # Traditional Cantonese Chinese
    cmn_hant_hk = Series.load(get_test_file_path("mnt/input/cmn-Hant-HK.srt"))
    cmn_hant_hk_merge = get_hanzi_merged(cmn_hant_hk)
    cmn_hant_hk_merge.save(get_output_path("mnt/output/cmn-Hant-HK_merge.srt"))
    cmn_hant_hk_simplify = get_hanzi_simplified(cmn_hant_hk)
    cmn_hant_hk_simplify.save(get_output_path("mnt/output/cmn-Hant-HK_simplify.srt"))
    cmn_hant_hk_merge_simplify = get_hanzi_merged(cmn_hant_hk_simplify)
    cmn_hant_hk_merge_simplify.save(
        get_output_path("mnt/output/cmn-Hant-HK_merge_simplify.srt")
    )

    # English
    en_us = Series.load(get_test_file_path("mnt/input/en-US.srt"))
    en_us_clean = get_english_cleaned(en_us)
    en_us_clean.save(get_output_path("mnt/output/en-US_clean.srt"))
    en_us_merge = get_english_merged(en_us)
    en_us_merge.save(get_output_path("mnt/output/en-US_merge.srt"))
    en_us_clean_merge = get_english_merged(en_us_clean)
    en_us_clean_merge.save(get_output_path("mnt/output/en-US_clean_merge.srt"))

    # Bilingual Simplified Cantonese Chinese and English
    en_us_clean_merge = get_english_merged(en_us_clean)
    cmn_hant_merge_simplify = get_hanzi_merged(cmn_hant_hk_simplify)
    cmn_hans_hk_en_us = get_synced_series(cmn_hant_merge_simplify, en_us_clean_merge)
    cmn_hans_hk_en_us.save(get_output_path("mnt/output/cmn-Hans-HK_en-US.srt"))
