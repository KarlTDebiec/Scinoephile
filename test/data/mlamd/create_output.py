#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""
from __future__ import annotations

from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import get_hanzi_cleaned, get_hanzi_flattened
from scinoephile.core.synchronization import get_synced_series
from scinoephile.image import ImageSeries
from scinoephile.image.validation import validate_ocr_hanzi
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    input_dir = test_data_root / "mlamd" / "input"
    output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(2)

    # Simplified Standard Chinese
    cmn_hans = Series.load(output_dir / "cmn-Hans" / "cmn-Hans.srt")
    cmn_hans = get_hanzi_cleaned(cmn_hans)
    cmn_hans.save(output_dir / "cmn-Hans" / "cmn-Hans.srt")

    cmn_hans = ImageSeries.load(output_dir / "cmn-Hans")
    validate_ocr_hanzi(cmn_hans, output_dir / "cmn-Hans_validation")

    # Traditional Standard Chinese
    cmn_hant = Series.load(output_dir / "cmn-Hant" / "cmn-Hant.srt")
    cmn_hant = get_hanzi_cleaned(cmn_hant)
    cmn_hant = get_hanzi_flattened(cmn_hant)
    cmn_hant.save(output_dir / "cmn-Hant" / "cmn-Hant.srt")

    # English
    eng = Series.load(output_dir / "eng" / "eng.srt")
    eng = get_english_cleaned(eng)
    eng = get_english_flattened(eng)
    eng.save(output_dir / "eng" / "eng.srt")

    # Bilingual Simplified Standard Chinese and English
    cmn_hans_eng = get_synced_series(cmn_hans, eng)
    cmn_hans_eng.save(output_dir / "cmn-Hans_eng.srt")
