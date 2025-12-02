#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.proofing."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.proofing import ProofingLLMQueryer, ProofingTestCase
from scinoephile.testing import skip_if_ci, test_data_root
from test.data.mlamd import mlamd_proof_test_cases  # noqa: F401


@pytest.fixture
def proofing_llm_queryer_few_shot() -> ProofingLLMQueryer:
    """LLMQueryer with few-shot examples."""
    return ProofingLLMQueryer(
        prompt_test_cases=[tc for tc in mlamd_proof_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def proofing_llm_queryer_zero_shot() -> ProofingLLMQueryer:
    """LLMQueryer with no examples."""
    return ProofingLLMQueryer(cache_dir_path=test_data_root / "cache")


async def _test_proofing(queryer: ProofingLLMQueryer, test_case: ProofingTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = await queryer.call_async(test_case.query)
    if test_case.difficulty < 3:
        assert answer.yuewen_proofread == test_case.yuewen_proofread, answer.note
        if test_case.yuewen != test_case.yuewen_proofread:
            assert len(answer.note) > 0  # Ensure that a note was generated


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("proofer_few_shot"),
        # skip_if_ci(flaky())("proofer_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_proof_test_cases if tc.verified]
)
async def test_proofing_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofer: ProofingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_proofing(proofer, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("proofer_few_shot"),
        # skip_if_ci(flaky())("proofer_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case",
    [tc for tc in mlamd_proof_test_cases if tc.difficulty >= 2 and tc.verified],
)
async def test_proofing_mlamd_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofer: ProofingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_proofing(proofer, test_case)
