#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import (
    EnglishProofer,
    get_english_cleaned,
    get_english_flattened,
    get_english_proofed,
)
from scinoephile.core.hanzi import (
    get_hanzi_cleaned,
    get_hanzi_converted,
    get_hanzi_flattened,
)
from scinoephile.core.synchronization import get_synced_series
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    input_dir = test_data_root / "t" / "input"
    output_dir = test_data_root / "t" / "output"
    set_logging_verbosity(2)

    # 简体中文
    zho_hans = Series.load(input_dir / "zho-Hans.srt")
    zho_hans_clean = get_hanzi_cleaned(zho_hans)
    zho_hans_clean.save(output_dir / "zho-Hans_clean.srt")
    zho_hans_flatten = get_hanzi_flattened(zho_hans)
    zho_hans_flatten.save(output_dir / "zho-Hans_flatten.srt")
    zho_hans_clean_flatten = get_hanzi_flattened(zho_hans_clean)
    zho_hans_clean_flatten.save(output_dir / "zho-Hans_clean_flatten.srt")

    # 繁體中文
    zho_hant = Series.load(input_dir / "zho-Hant.srt")
    zho_hant_simplify = get_hanzi_converted(zho_hant)
    zho_hant_simplify.save(output_dir / "zho-Hant_simplify.srt")

    # English
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(output_dir / "eng_flatten.srt")
    proofer = EnglishProofer(
        test_case_path=test_data_root / "t" / "core" / "english" / "proof.py",
    )
    eng_proof = get_english_proofed(eng, proofer)
    eng_proof.save(output_dir / "eng_proof.srt")
    eng_proof_clean = get_english_cleaned(eng_proof)
    eng_proof_clean_flatten = get_english_flattened(eng_proof_clean)
    eng_proof_clean_flatten.save(output_dir / "eng_proof_clean_flatten.srt")

    # Bilingual 简体中文 and English
    zho_hans_eng = get_synced_series(zho_hans_flatten, eng_proof_clean_flatten)
    zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")
