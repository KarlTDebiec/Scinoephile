#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.english."""

from __future__ import annotations

import pytest
from data.kob.test_cases.proofing import kob_proof_test_cases

from scinoephile.core.english.proofing import EnglishProofLLMQueryer
from scinoephile.testing import test_data_root


@pytest.fixture
def english_proof_llm_queryer_few_shot() -> EnglishProofLLMQueryer:
    """LLMQueryer with few-shot examples."""
    return EnglishProofLLMQueryer(
        prompt_test_cases=[tc for tc in kob_proof_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def english_proof_llm_queryer_zero_shot() -> EnglishProofLLMQueryer:
    """LLMQueryer with no examples."""
    return EnglishProofLLMQueryer(cache_dir_path=test_data_root / "cache")
