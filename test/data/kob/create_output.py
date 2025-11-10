#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import (
    EnglishProofer,
    get_english_cleaned,
    get_english_flattened,
    get_english_proofed,
)
from scinoephile.core.synchronization import get_synced_series
from scinoephile.core.zhongwen import (
    OpenCCConfig,
    get_zhongwen_cleaned,
    get_zhongwen_converted,
    get_zhongwen_flattened,
)
from scinoephile.testing import test_data_root

if __name__ == "__main__":
    input_dir = test_data_root / "kob" / "input"
    output_dir = test_data_root / "kob" / "output"
    set_logging_verbosity(2)

    # 简体粵文
    yue_hans = Series.load(input_dir / "yue-Hans.srt")
    yue_hans_clean = get_zhongwen_cleaned(yue_hans)
    yue_hans_clean.save(output_dir / "yue-Hans_clean.srt")
    yue_hans_flatten = get_zhongwen_flattened(yue_hans)
    yue_hans_flatten.save(output_dir / "yue-Hans_flatten.srt")
    yue_hans_clean_flatten = get_zhongwen_flattened(yue_hans_clean)
    yue_hans_clean_flatten.save(output_dir / "yue-Hans_clean_flatten.srt")

    # 繁體粵文
    yue_hant = Series.load(input_dir / "yue-Hant.srt")
    yue_hant_simplify = get_zhongwen_converted(yue_hant, OpenCCConfig.hk2s)
    yue_hant_simplify.save(output_dir / "yue-Hant_simplify.srt")

    # English
    eng = Series.load(input_dir / "eng.srt")
    eng_clean = get_english_cleaned(eng)
    eng_clean.save(output_dir / "eng_clean.srt")
    eng_flatten = get_english_flattened(eng)
    eng_flatten.save(output_dir / "eng_flatten.srt")
    proofer = EnglishProofer(
        test_case_path=test_data_root / "kob" / "core" / "english" / "proof.py",
    )
    eng_proof = get_english_proofed(eng, proofer)
    eng_proof.save(output_dir / "eng_proof.srt")
    eng_proof_clean = get_english_cleaned(eng_proof)
    eng_proof_clean_flatten = get_english_flattened(eng_proof_clean)
    eng_proof_clean_flatten.save(output_dir / "eng_proof_clean_flatten.srt")

    # Bilingual 简体粵文 and English
    yue_hans_eng = get_synced_series(yue_hans_clean_flatten, eng_proof_clean_flatten)
    yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")
