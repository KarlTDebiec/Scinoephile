#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.shifting."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.shifting import Shifter, ShiftTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import skip_if_ci
from test.data.mlamd import mlamd_shift_test_cases  # noqa: F401


@pytest.fixture
def shifter_few_shot() -> Shifter:
    """LLMQueryer with few-shot examples."""
    return Shifter(
        examples=[m for m in mlamd_shift_test_cases if m.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def shifter_zero_shot() -> Shifter:
    """LLMQueryer with no examples."""
    return Shifter(cache_dir_path=test_data_root / "cache")


def _test_shifting(queryer: Shifter, test_case: ShiftTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = queryer(test_case.query)
    assert answer.one_yuewen_shifted == test_case.one_yuewen_shifted
    assert answer.two_yuewen_shifted == test_case.two_yuewen_shifted


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("shifter_few_shot"),
        # skip_if_ci(flaky())("shifter_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_shift_test_cases)
def test_shifting_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ShiftTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    shifter: Shifter = request.getfixturevalue(fixture_name)
    _test_shifting(shifter, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("shifter_few_shot"),
        # skip_if_ci(flaky())("shifter_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_shift_test_cases if tc.difficulty >= 1]
)
def test_shifting_mlamd_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ShiftTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    shifter: Shifter = request.getfixturevalue(fixture_name)
    _test_shifting(shifter, test_case)
