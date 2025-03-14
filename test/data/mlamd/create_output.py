#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""
from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import get_hanzi_cleaned, get_hanzi_flattened
from scinoephile.core.synchronization import get_synced_series

if __name__ == "__main__":
    data_root = package_root.parent / "test" / "data" / "mlamd"
    set_logging_verbosity(2)

    # Simplified Standard Chinese
    cmn_hans = Series.load(data_root / "output" / "cmn-Hans" / "cmn-Hans.srt")
    cmn_hans = get_hanzi_cleaned(cmn_hans)
    cmn_hans = get_hanzi_flattened(cmn_hans)
    cmn_hans.save(data_root / "output" / "cmn-Hans" / "cmn-Hans.srt")

    # Traditional Standard Chinese
    cmn_hant = Series.load(data_root / "output" / "cmn-Hant" / "cmn-Hant.srt")
    cmn_hant = get_hanzi_cleaned(cmn_hant)
    cmn_hant = get_hanzi_flattened(cmn_hant)
    cmn_hant.save(data_root / "output" / "cmn-Hant" / "cmn-Hant.srt")

    # English
    eng = Series.load(data_root / "output" / "eng" / "eng.srt")
    eng = get_english_cleaned(eng)
    eng = get_english_flattened(eng)
    eng.save(data_root / "output" / "eng" / "eng.srt")

    # Bilingual Simplified Standard Chinese and English
    cmn_hans_eng = get_synced_series(cmn_hans, eng)
    cmn_hans_eng.save(data_root / "output" / "cmn-Hans_eng.srt")
