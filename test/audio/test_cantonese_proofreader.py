#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseProofer."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese import CantoneseProofer
from scinoephile.audio.cantonese.models import ProofTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_proof_test_cases  # noqa: F401


@pytest.fixture
def cantonese_proofer_few_shot() -> CantoneseProofer:
    """CantoneseProofer with few-shot examples."""
    return CantoneseProofer(
        examples=[m for m in mlamd_proof_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def cantonese_proofer_zero_shot() -> CantoneseProofer:
    """CantoneseProofer with no examples."""
    return CantoneseProofer(cache_dir_path=test_data_root / "cache")


def _test_proofread(cantonese_proofer: CantoneseProofer, test_case: ProofTestCase):
    """Test CantoneseProofer.

    Arguments:
        cantonese_proofer: F with which to test
        test_case: Query and expected answer
    """
    answer = cantonese_proofer(test_case.query)
    assert answer.yuewen_proofread == test_case.yuewen_proofread
    if test_case.yuewen != test_case.yuewen_proofread:
        assert len(answer.note) > 0  # Ensure that a note was generated


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("cantonese_proofer_few_shot"),
        skip_if_ci(flaky())("cantonese_proofer_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_proof_test_cases)
def test_proofread_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofTestCase
):
    """Test CantoneseProofer with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofer: CantoneseProofer = request.getfixturevalue(fixture_name)
    _test_proofread(proofer, test_case)
