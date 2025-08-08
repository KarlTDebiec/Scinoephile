#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.review."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.review import Reviewer
from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_review_test_cases  # noqa: F401

f


@pytest.fixture
def reviewer_few_shot() -> Reviewer:
    """LLMQueryer with few-shot examples."""
    return Reviewer(
        prompt_test_cases=[tc for tc in mlamd_review_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def reviewer_zero_shot() -> Reviewer:
    """LLMQueryer with no examples."""
    return Reviewer(cache_dir_path=test_data_root / "cache")


async def _test_review(queryer: Reviewer, test_case: ReviewTestCase):
    """Test.

    Arguments:
        queryer: LLMQueryer with which to test
        test_case: Query and expected answer
    """
    answer = await queryer.call(test_case.query, test_case.answer_cls, type(test_case))

    failures = []
    for field_name, expected_value in test_case.answer.model_dump().items():
        actual_value = getattr(answer, field_name)
        if actual_value != expected_value:
            failures.append(
                f"Field '{field_name}': expected {expected_value!r}, "
                f"got {actual_value!r}"
            )

    if failures:
        failure_report = "\n".join(failures)
        raise AssertionError(f"{len(failures)} mismatches:\n{failure_report}")


@pytest.mark.parametrize(
    "fixture_name",
    [
        # skip_if_ci()("reviewer_few_shot"),
        skip_if_ci(flaky())("reviewer_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_review_test_cases)
@pytest.mark.asyncio
async def test_review_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: ReviewTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    reviewer: Reviewer = request.getfixturevalue(fixture_name)
    await _test_review(reviewer, test_case)
