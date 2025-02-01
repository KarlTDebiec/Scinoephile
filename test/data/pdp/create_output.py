#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for PDP."""
from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import (
    get_hanzi_cleaned,
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from scinoephile.core.synchronization import get_synced_series
from scinoephile.testing.file import get_test_file_path

if __name__ == "__main__":

    def get_output_path(relative_path: str) -> Path:
        return package_root.parent / "test" / "data" / Path(relative_path)

    # Traditional Standard Chinese
    cmn_hant = Series.load(get_test_file_path("pdp/input/cmn-Hant.srt"))
    cmn_hant_clean = get_hanzi_cleaned(cmn_hant)
    cmn_hant_clean.save(get_output_path("pdp/output/cmn-Hant_clean.srt"))
    cmn_hant_flatten = get_hanzi_flattened(cmn_hant)
    cmn_hant_flatten.save(get_output_path("pdp/output/cmn-Hant_flatten.srt"))
    cmn_hant_simplify = get_hanzi_simplified(cmn_hant)
    cmn_hant_simplify.save(get_output_path("pdp/output/cmn-Hant_simplify.srt"))

    # Traditional Cantonese Chinese
    yue_hant = Series.load(get_test_file_path("pdp/input/yue-Hant.srt"))
    yue_hant_clean = get_hanzi_cleaned(yue_hant)
    yue_hant_clean.save(get_output_path("pdp/output/yue-Hant_clean.srt"))
    yue_hant_flatten = get_hanzi_flattened(yue_hant)
    yue_hant_flatten.save(get_output_path("pdp/output/yue-Hant_flatten.srt"))
    yue_hant_simplify = get_hanzi_simplified(yue_hant)
    yue_hant_simplify.save(get_output_path("pdp/output/yue-Hant_simplify.srt"))
    yue_hant_clean_flatten_simplify = get_hanzi_simplified(
        get_hanzi_flattened(yue_hant_clean)
    )
    yue_hant_clean_flatten_simplify.save(
        get_output_path("pdp/output/yue-Hant_clean_flatten_simplify.srt")
    )

    # English
    eng = Series.load(get_test_file_path("pdp/input/eng.srt"))
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(get_output_path("pdp/output/eng_clean.srt"))
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(get_output_path("pdp/output/eng_flatten.srt"))
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(get_output_path("pdp/output/eng_clean_flatten.srt"))

    # Bilingual Simplified Cantonese Chinese and English
    yue_hans_eng = get_synced_series(yue_hant_clean_flatten_simplify, eng_clean_flatten)
    yue_hans_eng.save(get_output_path("pdp/output/yue-Hans_eng.srt"))
