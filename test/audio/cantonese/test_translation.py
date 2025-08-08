#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.cantonese.translation."""

from __future__ import annotations

import pytest

from scinoephile.audio.cantonese.translation import Translator
from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase
from scinoephile.testing import test_data_root
from scinoephile.testing.mark import flaky, skip_if_ci
from test.data.mlamd import mlamd_translate_test_cases  # noqa: F401


@pytest.fixture
def translator_few_shot() -> Translator:
    """LLMQueryer with few-shot examples."""
    return Translator(
        prompt_test_cases=[tc for tc in mlamd_translate_test_cases if tc.prompt],
        cache_dir_path=test_data_root / "cache",
    )


@pytest.fixture
def translator_zero_shot() -> Translator:
    """LLMQueryer with no examples."""
    return Translator(cache_dir_path=test_data_root / "cache")


async def _test_translation(queryer: Translator, test_case: TranslateTestCase):
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
        skip_if_ci(flaky())("translator_few_shot"),
        # skip_if_ci(flaky())("translator_zero_shot"),
    ],
)
@pytest.mark.parametrize("test_case", mlamd_translate_test_cases)
@pytest.mark.asyncio
async def test_translation_mlamd(
    request: pytest.FixtureRequest, fixture_name: str, test_case: TranslateTestCase
):
    """Test with MLAMD test cases.

    Arguments:
        request: Pytest fixture request
        fixture_name: Name of fixture with which to test
        test_case: Query and expected answer
    """
    translator: Translator = request.getfixturevalue(fixture_name)
    await _test_translation(translator, test_case)
