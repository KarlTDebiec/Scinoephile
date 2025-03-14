#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for PDP."""
from __future__ import annotations

from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import (
    get_hanzi_cleaned,
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from scinoephile.core.synchronization import get_synced_series
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    input_dir = test_data_root / "pdp" / "input"
    output_dir = test_data_root / "pdp" / "output"
    set_logging_verbosity(2)

    # Traditional Standard Chinese
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_clean = get_hanzi_cleaned(zho_hant)
    zho_hant_clean.save(output_dir / "zho-Hant_clean.srt")
    zho_hant_flatten = get_hanzi_flattened(zho_hant)
    zho_hant_flatten.save(output_dir / "zho-Hant_flatten.srt")
    zho_hant_simplify = get_hanzi_simplified(zho_hant)
    zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")

    # Traditional Cantonese Chinese
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_clean = get_hanzi_cleaned(yue_hant)
    yue_hant_clean.save(output_dir / "yue-Hant_clean.srt")
    yue_hant_flatten = get_hanzi_flattened(yue_hant)
    yue_hant_flatten.save(output_dir / "yue-Hant_flatten.srt")
    yue_hant_simplify = get_hanzi_simplified(yue_hant)
    yue_hant_simplify.save(output_dir / "yue-Hant_simplify.srt")
    yue_hant_clean_flatten_simplify = get_hanzi_simplified(
        get_hanzi_flattened(yue_hant_clean)
    )
    yue_hant_clean_flatten_simplify.save(
        output_dir / "yue-Hant_clean_flatten_simplify.srt"
    )

    # English
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(output_dir / "eng_flatten.srt")
    eng_clean_flatten = get_english_flattened(eng_clean)
    eng_clean_flatten.save(output_dir / "eng_clean_flatten.srt")

    # Bilingual Simplified Cantonese Chinese and English
    yue_hans_eng = get_synced_series(yue_hant_clean_flatten_simplify, eng_clean_flatten)
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
