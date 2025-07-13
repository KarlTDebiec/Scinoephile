"""Tests of scinoephile.audio.transcription.CantoneseShifter."""

#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

import pytest

from scinoephile.audio.testing import ShiftTestCase
from scinoephile.audio.transcription import CantoneseShifter
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_shift_test_cases  # noqa: F401


@pytest.fixture
def cantonese_shifter_few_shot() -> CantoneseShifter:
    """CantoneseShifter with few-shot examples."""
    return CantoneseShifter(
        examples=[m for m in mlamd_shift_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def cantonese_shifter_zero_shot() -> CantoneseShifter:
    """CantoneseShifter with no examples."""
    return CantoneseShifter(cache_dir_path=test_data_root / "cache")


def _test_shift(cantonese_shifter: CantoneseShifter, test_case: ShiftTestCase):
    """Test CantoneseShifter.

    Arguments:
        cantonese_shifter: CantoneseShifter with which to test
        test_case: Query and expected answer
    """
    answer = cantonese_shifter(test_case.query)
    assert answer.one_yuewen_shifted == test_case.one_yuewen_shifted
    assert answer.two_yuewen_shifted == test_case.two_yuewen_shifted


@pytest.mark.parametrize(
    "shifter_fixture_name",
    [
        skip_if_ci()("cantonese_shifter_few_shot"),
        skip_if_ci(flaky())("cantonese_shifter_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_shift_test_cases)
def test_shift_mlamd(
    request: pytest.FixtureRequest, shifter_fixture_name: str, test_case: ShiftTestCase
):
    """Test CantoneseShifter with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        shifter_fixture_name: Name of CantoneseShifter fixture with which to test
        test_case: Query and expected answer
    """
    shifter: CantoneseShifter = request.getfixturevalue(shifter_fixture_name)
    _test_shift(shifter, test_case)
