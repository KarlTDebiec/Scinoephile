#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.english.test_get_english_proofed."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import get_english_proofed
from scinoephile.core.english.proofing import EnglishProofLLMQueryer
from scinoephile.testing import test_data_root
from test.data.kob import kob_english_proof_test_cases
from test.data.mlamd import mlamd_english_proof_test_cases


@pytest.fixture
def english_proof_llm_queryer_few_shot() -> EnglishProofLLMQueryer:
    """LLMQueryer with few-shot examples."""
    return EnglishProofLLMQueryer(
        prompt_test_cases=[tc for tc in kob_english_proof_test_cases if tc.prompt]
        + [tc for tc in mlamd_english_proof_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def english_proof_llm_queryer_zero_shot() -> EnglishProofLLMQueryer:
    """LLMQueryer with no examples."""
    return EnglishProofLLMQueryer(cache_dir_path=test_data_root / "cache")


def _test_get_english_proofed(series: Series, expected: Series):
    """Test get_english_proofed.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_english_proofed(series)

    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_english_proofed_kob(kob_eng: Series, kob_eng_proof: Series):
    """Test get_english_proofed with KOB English subtitles.

    Arguments:
        kob_eng: KOB English series fixture
        kob_eng_proof: Expected proofed KOB English series fixture
    """
    _test_get_english_proofed(kob_eng, kob_eng_proof)


def test_get_english_proofed_mlamd(mlamd_eng: Series, mlamd_eng_proof: Series):
    """Test get_english_proofed with MLAMD English subtitles.

    Arguments:
        mlamd_eng: MLAMD English series fixture
        mlamd_eng_proof: Expected proofed MLAMD English series fixture
    """
    _test_get_english_proofed(mlamd_eng, mlamd_eng_proof)
