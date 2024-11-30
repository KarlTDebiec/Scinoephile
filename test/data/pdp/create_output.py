#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for PDP."""
from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import get_hanzi_flattened, get_hanzi_simplified
from scinoephile.core.synchronization import get_synced_series
from scinoephile.testing.file import get_test_file_path

if __name__ == "__main__":

    def get_output_path(relative_path: str) -> Path:
        return package_root.parent / "test" / "data" / Path(relative_path)

    # Traditional Standard Chinese
    cmn_hant_hk = Series.load(get_test_file_path("pdp/input/cmn-Hant-HK.srt"))
    cmn_hant_hk_flatten = get_hanzi_flattened(cmn_hant_hk)
    cmn_hant_hk_flatten.save(get_output_path("pdp/output/cmn-Hant-HK_flatten.srt"))
    cmn_hant_hk_simplify = get_hanzi_simplified(cmn_hant_hk)
    cmn_hant_hk_simplify.save(get_output_path("pdp/output/cmn-Hant-HK_simplify.srt"))

    # Traditional Cantonese Chinese
    yue_hant_hk = Series.load(get_test_file_path("pdp/input/yue-Hant-HK.srt"))
    yue_hant_hk_flatten = get_hanzi_flattened(yue_hant_hk)
    yue_hant_hk_flatten.save(get_output_path("pdp/output/yue-Hant-HK_flatten.srt"))
    yue_hant_hk_simplify = get_hanzi_simplified(yue_hant_hk)
    yue_hant_hk_simplify.save(get_output_path("pdp/output/yue-Hant-HK_simplify.srt"))
    yue_hant_hk_flatten_simplify = get_hanzi_flattened(yue_hant_hk_simplify)
    yue_hant_hk_flatten_simplify.save(
        get_output_path("pdp/output/yue-Hant-HK_flatten_simplify.srt")
    )

    # English
    en_hk = Series.load(get_test_file_path("pdp/input/en-HK.srt"))
    en_hk_clean = get_english_cleaned(en_hk)
    en_hk_clean.save(get_output_path("pdp/output/en-HK_clean.srt"))
    en_hk_flatten = get_english_flattened(en_hk)
    en_hk_flatten.save(get_output_path("pdp/output/en-HK_flatten.srt"))
    en_hk_clean_flatten = get_english_flattened(en_hk_clean)
    en_hk_clean_flatten.save(get_output_path("pdp/output/en-HK_clean_flatten.srt"))

    # Bilingual Simplified Cantonese Chinese and English
    en_hk_clean_flatten = get_english_flattened(en_hk_clean)
    yue_hant_flatten_simplify = get_hanzi_flattened(yue_hant_hk_simplify)
    yue_hans_hk_en_hk = get_synced_series(
        yue_hant_flatten_simplify, en_hk_clean_flatten
    )
    yue_hans_hk_en_hk.save(get_output_path("pdp/output/yue-Hans-HK_en-HK.srt"))
