#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.distribution."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.distribution import DistributeTestCase, Distributor
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import skip_if_ci
from test.data.mlamd import mlamd_distribute_test_cases  # noqa: F401
from test.data.mnt.distribution import mnt_distribute_test_cases  # noqa: F401
from test.data.t.distribution import t_distribute_test_cases  # noqa: F401


@pytest.fixture
def distributor_few_shot() -> Distributor:
    """LLMQueryer with few-shot examples."""
    return Distributor(
        prompt_test_cases=[tc for tc in mlamd_distribute_test_cases if tc.prompt],
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
    if test_case.difficulty < 3:
        assert answer.yuewen_1_to_append == test_case.yuewen_1_to_append
        assert answer.yuewen_2_to_prepend == test_case.yuewen_2_to_prepend


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
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


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mlamd_distribute_test_cases if tc.difficulty >= 1]
)
def test_distribution_mlamd_difficult(
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


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mnt_distribute_test_cases)
def test_distribution_mnt(
    request: pytest.FixtureRequest, fixture_name: str, test_case: DistributeTestCase
):
    """Test with MNT test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    distributor: Distributor = request.getfixturevalue(fixture_name)
    _test_distribution(distributor, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in mnt_distribute_test_cases if tc.difficulty >= 1]
)
def test_distribution_mnt_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: DistributeTestCase
):
    """Test with MNT test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    distributor: Distributor = request.getfixturevalue(fixture_name)
    _test_distribution(distributor, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", t_distribute_test_cases)
def test_distribution_t(
    request: pytest.FixtureRequest, fixture_name: str, test_case: DistributeTestCase
):
    """Test with T test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    distributor: Distributor = request.getfixturevalue(fixture_name)
    _test_distribution(distributor, test_case)


@pytest.mark.parametrize(
    "fixture_name",
    [
        skip_if_ci()("distributor_few_shot"),
        # skip_if_ci(flaky())("distributor_zero_shot"),
    ],
)
@pytest.mark.parametrize(
    "test_case", [tc for tc in t_distribute_test_cases if tc.difficulty >= 1]
)
def test_distribution_t_difficult(
    request: pytest.FixtureRequest, fixture_name: str, test_case: DistributeTestCase
):
    """Test with T test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    distributor: Distributor = request.getfixturevalue(fixture_name)
    _test_distribution(distributor, test_case)
