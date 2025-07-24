#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.merging."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.merging import Merger, MergeTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_merge_test_cases  # noqa: F401


@pytest.fixture
def merger_few_shot() -> Merger:
    """LLMQueryer with few-shot examples."""
    return Merger(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def merger_zero_shot() -> Merger:
    """LLMQueryer with no examples."""
    return Merger(cache_dir_path=test_data_root / "cache")


def _test_merging(queryer: Merger, test_case: MergeTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = queryer(test_case.query)
    assert answer.yuewen_merged == test_case.yuewen_merged


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("merger_few_shot"),
        skip_if_ci(flaky())("merger_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_merge_test_cases)
def test_merging_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: MergeTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    merger: Merger = request.getfixturevalue(fixture_name)
    _test_merging(merger, test_case)
