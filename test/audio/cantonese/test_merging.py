#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.merging."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.merging import MergingLLMQueryer, MergingTestCase
from scinoephile.testing import skip_if_ci, test_data_root
from test.data.mlamd import mlamd_merge_test_cases  # noqa: F401


@pytest.fixture
def merging_llm_queryer_few_shot() -> MergingLLMQueryer:
    """LLMQueryer with few-shot examples."""
    return MergingLLMQueryer(
        prompt_test_cases=[tc for tc in mlamd_merge_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def merging_llm_queryer_zero_shot() -> MergingLLMQueryer:
    """LLMQueryer with no examples."""
    return MergingLLMQueryer(cache_dir_path=test_data_root / "cache")


async def _test_merging(queryer: MergingLLMQueryer, test_case: MergingTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    if test_case.difficulty < 3:
        answer = await queryer.call(test_case.query)
        assert answer.yuewen_merged == test_case.yuewen_merged


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("merger_few_shot"),
        # skip_if_ci(flaky())("merger_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_merge_test_cases if tc.verified]
)
@pytest.mark.asyncio
async def test_merging_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: MergingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    merger: MergingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_merging(merger, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("merger_few_shot"),
        # skip_if_ci(flaky())("merger_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case",
    [tc for tc in mlamd_merge_test_cases if tc.difficulty >= 2 and tc.verified],
)
@pytest.mark.asyncio
async def test_merging_mlamd_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: MergingTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    merger: MergingLLMQueryer = request.getfixturevalue(fixture_name)
    await _test_merging(merger, test_case)
