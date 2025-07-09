#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.runnables."""

from pprint import pformat

import pytest

from scinoephile.audio.transcription import CantoneseMerger
from scinoephile.testing import MergeTestCase
from scinoephile.testing.mark import flaky, skip_if_ci

from ..data.mlamd import mlamd_merge_test_cases  # noqa: F401


@pytest.fixture
def cantonese_merger_few_shot() -> CantoneseMerger:
    """CantoneseMerger with few-shot examples."""
    return CantoneseMerger(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt]
    )


@pytest.fixture
def cantonese_merger_zero_shot() -> CantoneseMerger:
    """CantoneseMerger with no examples."""
    return CantoneseMerger()


def _test_merge(cantonese_merger: CantoneseMerger, test_case: MergeTestCase):
    """Test merging of Cantonese and Yuewen text."""
    output = cantonese_merger.merge(test_case.zhongwen_input, test_case.yuewen_input)
    assert output == test_case.yuewen_output, pformat(test_case)


@pytest.mark.parametrize(
    "merger_fixture_name",
    [
        skip_if_ci()("cantonese_merger_few_shot"),
        skip_if_ci(flaky())("cantonese_merger_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_merge_test_cases)
def test_merge_mlamd(
    request: pytest.FixtureRequest, merger_fixture_name: str, test_case: MergeTestCase
):
    """Test merging of Cantonese and Yuewen text using MLAMD test cases."""
    merger: CantoneseMerger = request.getfixturevalue(merger_fixture_name)
    _test_merge(merger, test_case)
