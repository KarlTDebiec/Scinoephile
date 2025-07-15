#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseMerger."""

from __future__ import annotations

import pytest

from scinoephile.audio.testing import MergeTestCase
from scinoephile.audio.transcription import CantoneseMerger
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_merge_test_cases  # noqa: F401


@pytest.fixture
def cantonese_merger_few_shot() -> CantoneseMerger:
    """CantoneseMerger with few-shot examples."""
    return CantoneseMerger(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def cantonese_merger_zero_shot() -> CantoneseMerger:
    """CantoneseMerger with no examples."""
    return CantoneseMerger(cache_dir_path=test_data_root / "cache")


def _test_merge(cantonese_merger: CantoneseMerger, test_case: MergeTestCase):
    """Test CantoneseMerger.

    Arguments:
        cantonese_merger: CantoneseMerger with which to test
        test_case: Query and expected answer
    """
    answer = cantonese_merger(test_case.query)
    assert answer.yuewen_merged == test_case.yuewen_merged


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("cantonese_merger_few_shot"),
        skip_if_ci(flaky())("cantonese_merger_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_merge_test_cases)
def test_merge_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: MergeTestCase
):
    """Test CantoneseMerger with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    merger: CantoneseMerger = request.getfixturevalue(fixture_name)
    _test_merge(merger, test_case)
