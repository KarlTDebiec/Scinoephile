#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseSplitter."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese import CantoneseSplitter
from scinoephile.audio.testing import SplitTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_split_test_cases  # noqa: F401


@pytest.fixture
def cantonese_splitter_few_shot() -> CantoneseSplitter:
    """CantoneseSplitter with few-shot examples."""
    return CantoneseSplitter(
        examples=[m for m in mlamd_split_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def cantonese_splitter_zero_shot() -> CantoneseSplitter:
    """CantoneseSplitter with no examples."""
    return CantoneseSplitter(cache_dir_path=test_data_root / "cache")


def _test_split(cantonese_splitter: CantoneseSplitter, test_case: SplitTestCase):
    """Test CantoneseSplitter.

    Arguments:
        cantonese_splitter: CantoneseSplitter with which to test
        test_case: Query and expected answer
    """
    answer = cantonese_splitter(test_case.query)
    assert answer.one_yuewen_to_append == test_case.one_yuewen_to_append
    assert answer.two_yuewen_to_prepend == test_case.two_yuewen_to_prepend


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("cantonese_splitter_few_shot"),
        skip_if_ci(flaky())("cantonese_splitter_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_split_test_cases)
def test_split_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: SplitTestCase
):
    """Test CantoneseSplitter with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    splitter: CantoneseSplitter = request.getfixturevalue(fixture_name)
    _test_split(splitter, test_case)
