#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""
from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import (
    get_hanzi_cleaned,
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from scinoephile.core.synchronization import get_synced_series

if __name__ == "__main__":
    data_root = package_root.parent / "test" / "data" / "mnt"
    set_logging_verbosity(2)

    # Traditional Cantonese Chinese
    cmn_hant = Series.load(data_root / "input" / "cmn-Hant.srt")
    cmn_hant_clean = get_hanzi_cleaned(cmn_hant)
    cmn_hant_clean.save(data_root / "output" / "cmn-Hant_clean.srt")
    cmn_hant_flatten = get_hanzi_flattened(cmn_hant)
    cmn_hant_flatten.save(data_root / "output" / "cmn-Hant_flatten.srt")
    cmn_hant_simplify = get_hanzi_simplified(cmn_hant)
    cmn_hant_simplify.save(data_root / "output" / "cmn-Hant_simplify.srt")
    cmn_hant_clean_flatten_simplify = get_hanzi_simplified(
        get_hanzi_flattened(cmn_hant_clean)
    )
    cmn_hant_clean_flatten_simplify.save(
        data_root / "output" / "cmn-Hant_clean_flatten_simplify.srt"
    )

    # English
    eng = Series.load(data_root / "input" / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(data_root / "output" / "eng_clean.srt")
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(data_root / "output" / "eng_flatten.srt")
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(data_root / "output" / "eng_clean_flatten.srt")

    # Bilingual Simplified Cantonese Chinese and English
    cmn_hans_eng = get_synced_series(cmn_hant_clean_flatten_simplify, eng_clean_flatten)
    cmn_hans_eng.save(data_root / "output" / "cmn-Hant_eng.srt")
