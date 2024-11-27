#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""
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
    en_hk = Series.load(get_test_file_path("t/input/en-HK.srt"))
    en_hk_clean = get_english_cleaned(en_hk)
    en_hk_clean.save(get_output_path("t/output/en-HK_clean.srt"))
    en_hk_merge = get_english_merged(en_hk)
    en_hk_merge.save(get_output_path("t/output/en-HK_merge.srt"))

    # Simplified Chinese
    cmn_hans_hk = Series.load(get_test_file_path("t/input/cmn-Hans-HK.srt"))
    cmn_hans_hk_merge = get_hanzi_merged(cmn_hans_hk)
    cmn_hans_hk_merge.save(get_output_path("t/output/cmn-Hans-HK_merge.srt"))

    # Traditional Chinese
    cmn_hant_hk = Series.load(get_test_file_path("t/input/cmn-Hant-HK.srt"))
    cmn_hant_hk_simplify = get_hanzi_simplified(cmn_hant_hk)
    cmn_hant_hk_simplify.save(get_output_path("t/output/cmn-Hant-HK_simplify.srt"))

    # Bilingual Simplified Chinese and English
    en_hk_clean_merge = get_english_merged(en_hk_clean)
    cmn_hans_hk_en_hk = get_synced_series(cmn_hans_hk_merge, en_hk_clean_merge)
    cmn_hans_hk_en_hk.save(get_output_path("t/output/cmn-Hans-HK_en-HK.srt"))
