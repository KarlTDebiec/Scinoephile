#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseProofreader."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese import CantoneseProofreader
from scinoephile.audio.testing import ProofreadTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_proofread_test_cases  # noqa: F401


@pytest.fixture
def cantonese_proofreader_few_shot() -> CantoneseProofreader:
    """CantoneseProofreader with few-shot examples."""
    return CantoneseProofreader(
        examples=[m for m in mlamd_proofread_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def cantonese_proofreader_zero_shot() -> CantoneseProofreader:
    """CantoneseProofreader with no examples."""
    return CantoneseProofreader(cache_dir_path=test_data_root / "cache")


def _test_proofread(
    cantonese_proofreader: CantoneseProofreader, test_case: ProofreadTestCase
):
    """Test CantoneseProofreader.

    Arguments:
        cantonese_proofreader: CantoneseProofreader with which to test
        test_case: Query and expected answer
    """
    answer = cantonese_proofreader(test_case.query)
    assert answer.yuewen_proofread == test_case.yuewen_proofread
    if test_case.yuewen != test_case.yuewen_proofread:
        assert len(answer.note) > 0  # Ensure that a note was generated


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("cantonese_proofreader_few_shot"),
        skip_if_ci(flaky())("cantonese_proofreader_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_proofread_test_cases)
def test_proofread_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ProofreadTestCase
):
    """Test CantoneseProofreader with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    proofreader: CantoneseProofreader = request.getfixturevalue(fixture_name)
    _test_proofread(proofreader, test_case)
