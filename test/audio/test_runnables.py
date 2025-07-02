#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.runnables."""

from pprint import pformat

import pytest
from data.mlamd import mlamd_merge_test_cases

from scinoephile.audio.models import MergePayload
from scinoephile.audio.runnables import CantoneseMergerInner
from scinoephile.testing import MergeTestCase


@pytest.fixture
def cantonese_merger_few_shot() -> CantoneseMergerInner:
    return CantoneseMergerInner(
        examples=[m for m in mlamd_merge_test_cases if m.include_in_prompt]
    )


@pytest.fixture
def cantonese_merger_zero_shot() -> CantoneseMergerInner:
    return CantoneseMergerInner()


def _test_merge(cantonese_merger: CantoneseMergerInner, test_case: MergeTestCase):
    payload = MergePayload(
        zhongwen=test_case.zhongwen_input,
        yuewen=test_case.yuewen_input,
    )
    output = cantonese_merger.invoke(payload)
    assert output == test_case.yuewen_output, pformat(test_case)


@pytest.mark.parametrize(
    "merger_fixture_name",
    [
        "cantonese_merger_few_shot",
        "cantonese_merger_zero_shot",
    ],
)
@pytest.mark.parametrize("test_case", mlamd_merge_test_cases)
def test_merge_mlamd(
    request: pytest.FixtureRequest, merger_fixture_name: str, test_case: MergeTestCase
):
    merger: CantoneseMergerInner = request.getfixturevalue(merger_fixture_name)
    _test_merge(merger, test_case)
