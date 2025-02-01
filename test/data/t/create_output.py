#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""
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

    # Simplified Standard Chinese
    cmn_hans = Series.load(get_test_file_path("t/input/cmn-Hans.srt"))
    cmn_hans_clean = get_hanzi_cleaned(cmn_hans)
    cmn_hans_clean.save(get_output_path("t/output/cmn-Hans_clean.srt"))
    cmn_hans_flatten = get_hanzi_flattened(cmn_hans)
    cmn_hans_flatten.save(get_output_path("t/output/cmn-Hans_flatten.srt"))
    cmn_hans_clean_flatten = get_hanzi_flattened(cmn_hans_clean)
    cmn_hans_clean_flatten.save(get_output_path("t/output/cmn-Hans_clean_flatten.srt"))

    # Traditional Standard Chinese
    cmn_hant = Series.load(get_test_file_path("t/input/cmn-Hant.srt"))
    cmn_hant_simplify = get_hanzi_simplified(cmn_hant)
    cmn_hant_simplify.save(get_output_path("t/output/cmn-Hant_simplify.srt"))

    # English
    eng = Series.load(get_test_file_path("t/input/eng.srt"))
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(get_output_path("t/output/eng_clean.srt"))
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(get_output_path("t/output/eng_flatten.srt"))
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(get_output_path("t/output/eng_clean_flatten.srt"))

    # Bilingual Simplified Chinese and English
    cmn_hans_eng = get_synced_series(cmn_hans_flatten, eng_clean_flatten)
    cmn_hans_eng.save(get_output_path("t/output/cmn-Hans_eng.srt"))
