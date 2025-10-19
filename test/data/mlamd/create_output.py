#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import get_hanzi_cleaned, get_hanzi_flattened
from scinoephile.core.synchronization import get_synced_series
from scinoephile.image import ValidationManager
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    input_dir = test_data_root / "mlamd" / "input"
    output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(2)

    # 简体中文
    zho_hans = Series.load(output_dir / "zho-Hans" / "zho-Hans.srt")
    zho_hans = get_hanzi_cleaned(zho_hans)
    zho_hans.save(output_dir / "zho-Hans" / "zho-Hans.srt")

    ValidationManager(
        output_dir / "zho-Hans",
        output_dir / "zho-Hans_validation",
        False,
    ).validate()

    # 繁體中文
    zho_hant = Series.load(output_dir / "zho-Hant" / "zho-Hant.srt")
    zho_hant = get_hanzi_cleaned(zho_hant)
    zho_hant = get_hanzi_flattened(zho_hant)
    zho_hant.save(output_dir / "zho-Hant" / "zho-Hant.srt")

    ValidationManager(
        output_dir / "zho-Hant",
        output_dir / "zho-Hant_validation",
        False,
    ).validate()

    # English
    eng = Series.load(output_dir / "eng" / "eng.srt")
    eng = get_english_cleaned(eng)
    eng = get_english_flattened(eng)
    eng.save(output_dir / "eng" / "eng.srt")

    # Bilingual 简体中文 and English
    zho_hans_eng = get_synced_series(zho_hans, eng)
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")

    # Bilingual 简体粤文 and English
    if (output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt").exists():
        yue_hans = Series.load(output_dir / "yue-Hans_audio" / "yue-Hans_audio.srt")
        yue_hans_eng = get_synced_series(yue_hans, eng)
        yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
