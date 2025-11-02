#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

from data.kob import kob_english_proof_test_cases

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english import get_english_proofed
from scinoephile.core.english.proofing import EnglishProofer
from scinoephile.testing import test_data_root
from test.data.mlamd import mlamd_english_proof_test_cases

if __name__ == "__main__":
    input_dir = test_data_root / "mlamd" / "input"
    output_dir = test_data_root / "mlamd" / "output"
    set_logging_verbosity(2)

    # English
    eng = Series.load(input_dir / "eng.srt")
    proofer = EnglishProofer(
        proof_test_cases=kob_english_proof_test_cases + mlamd_english_proof_test_cases,
        test_case_path=test_data_root / "mlamd" / "core" / "english" / "proof.py",
    )
    eng_proof = get_english_proofed(eng, proofer, stop_at_idx=4)
    eng_proof.save(output_dir / "eng_proof.srt")
