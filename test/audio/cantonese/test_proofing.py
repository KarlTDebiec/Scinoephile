#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.proofing."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.proofing import Proofer, ProofTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import skip_if_ci
from test.data.mlamd import mlamd_proof_test_cases  # noqa: F401


@pytest.fixture
def proofer_few_shot() -> Proofer:
    """LLMQueryer with few-shot examples."""
    return Proofer(
        prompt_test_cases=[m for m in mlamd_proof_test_cases if m.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def proofer_zero_shot() -> Proofer:
    """LLMQueryer with no examples."""
    return Proofer(cache_dir_path=test_data_root / "cache")


def _test_proofing(queryer: Proofer, test_case: ProofTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = queryer(test_case.query)
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
@pytest.mark.parametrize("test_case", mlamd_proof_test_cases)
def test_proofing_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofer: Proofer = request.getfixturevalue(fixture_name)
    _test_proofing(proofer, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("proofer_few_shot"),
        # skip_if_ci(flaky())("proofer_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_proof_test_cases if tc.difficulty > 1]
)
def test_proofing_mlamd_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofer: Proofer = request.getfixturevalue(fixture_name)
    _test_proofing(proofer, test_case)
