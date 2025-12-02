#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.shifting."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.shifting import ShiftingLLMQueryer, ShiftingTestCase
from scinoephile.testing import skip_if_ci, test_data_root
from test.data.mlamd import mlamd_shift_test_cases  # noqa: F401


@pytest.fixture
def shifting_llm_queryer_few_shot() -> ShiftingLLMQueryer:
    """LLMQueryer with few-shot examples."""
    return ShiftingLLMQueryer(
        prompt_test_cases=[tc for tc in mlamd_shift_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def shifting_llm_queryer_zero_shot() -> ShiftingLLMQueryer:
    """LLMQueryer with no examples."""
    return ShiftingLLMQueryer(cache_dir_path=test_data_root / "cache")


async def _test_shifting(queryer: ShiftingLLMQueryer, test_case: ShiftingTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = await queryer.call_async(test_case.query)
    if test_case.difficulty < 3:
        assert answer.yuewen_1_shifted == test_case.yuewen_1_shifted
        assert answer.yuewen_2_shifted == test_case.yuewen_2_shifted


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("shifter_few_shot"),
        # skip_if_ci(flaky())("shifter_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_shift_test_cases if tc.verified]
)
@pytest.mark.asyncio
async def test_shifting_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ShiftingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    shifter: ShiftingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_shifting(shifter, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("shifter_few_shot"),
        # skip_if_ci(flaky())("shifter_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case",
    [tc for tc in mlamd_shift_test_cases if tc.difficulty >= 1 and tc.verified],
)
@pytest.mark.asyncio
async def test_shifting_mlamd_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ShiftingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    shifter: ShiftingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_shifting(shifter, test_case)
