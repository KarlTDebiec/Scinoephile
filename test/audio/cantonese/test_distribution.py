#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.distribution."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.distribution import DistributeTestCase, Distributor
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_distribute_test_cases  # noqa: F401


@pytest.fixture
def distributor_few_shot() -> Distributor:
    """LLMQueryer with few-shot examples."""
    return Distributor(
        examples=[m for m in mlamd_distribute_test_cases if m.include_in_prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def distributor_zero_shot() -> Distributor:
    """LLMQueryer with no examples."""
    return Distributor(cache_dir_path=test_data_root / "cache")


def _test_distribution(queryer: Distributor, test_case: DistributeTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = queryer(test_case.query)
    assert answer.one_yuewen_to_append == test_case.one_yuewen_to_append
    assert answer.two_yuewen_to_prepend == test_case.two_yuewen_to_prepend


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_distribute_test_cases)
def test_distribution_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: DistributeTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    distributor: Distributor = request.getfixturevalue(fixture_name)
    _test_distribution(distributor, test_case)
