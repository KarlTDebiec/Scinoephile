#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from typing import cast

from scinoephile.core.english.proofreading import (
    EnglishProofreadingPrompt2,
    EnglishProofreadingTestCase2,
)
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.testing import test_data_root

title = "kob"


@cache
def get_proofreading_test_cases(
    prompt_cls: type[EnglishProofreadingPrompt2] = EnglishProofreadingPrompt2,
) -> list[EnglishProofreadingTestCase2]:
    """Load English proofreading test cases from JSON.

    Arguments:
        prompt_cls: text strings to be used for corresponding with LLM
    Returns:
        list of English proofreading test cases
    """
    path = test_data_root / title / "core" / "english" / "proofreading.json"
    test_cases = load_test_cases_from_json(
        path, EnglishProofreadingTestCase2, prompt_cls=prompt_cls
    )

    return cast(list[EnglishProofreadingTestCase2], test_cases)
