#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseSplitter."""

import pytest

from scinoephile.audio.testing import SplitTestCase
from scinoephile.audio.transcription import CantoneseSplitter
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_split_test_cases  # noqa: F401


@pytest.fixture
def cantonese_splitter_few_shot() -> CantoneseSplitter:
    """CantoneseSplitter with few-shot examples."""
    return CantoneseSplitter(
        examples=[m for m in mlamd_split_test_cases if m.include_in_prompt],
        print_test_case=True,
    )


@pytest.fixture
def cantonese_splitter_zero_shot() -> CantoneseSplitter:
    """CantoneseSplitter with no examples."""
    return CantoneseSplitter(print_test_case=True)


def _test_split(cantonese_splitter: CantoneseSplitter, test_case: SplitTestCase):
    """Test CantoneseSplitter.

    Arguments:
        cantonese_splitter: CantoneseSplitter with which to test
        test_case: Inputs and expected outputs
    """
    yuewen_one_output, yuewen_two_output = cantonese_splitter(
        test_case.zhongwen_one_input,
        test_case.yuewen_one_input,
        test_case.yuewen_one_overlap,
        test_case.zhongwen_two_input,
        test_case.yuewen_two_input,
        test_case.yuewen_two_overlap,
        test_case.yuewen_ambiguous_input,
    )
    assert yuewen_one_output == test_case.yuewen_one_output
    assert yuewen_two_output == test_case.yuewen_two_output


@pytest.mark.parametrize(
    "splitter_fixture_name",
    [
        skip_if_ci()("cantonese_splitter_few_shot"),
        skip_if_ci(flaky())("cantonese_splitter_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_split_test_cases)
def test_split_mlamd(
    request: pytest.FixtureRequest,
    splitter_fixture_name: str,
    test_case: SplitTestCase,
):
    """Test CantoneseSplitter with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        splitter_fixture_name: Name of CantoneseSplitter fixture with which to test
        test_case: Inputs and expected outputs
    """
    splitter: CantoneseSplitter = request.getfixturevalue(splitter_fixture_name)
    _test_split(splitter, test_case)
