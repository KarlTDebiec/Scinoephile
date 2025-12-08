#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

import json
from functools import cache

from scinoephile.core.abcs.functions import load_test_cases_from_json
from scinoephile.core.english.proofreading import (
    EnglishProofreadingPrompt2,
    EnglishProofreadingTestCase2,
)
from scinoephile.testing import test_data_root

title = "kob"


@cache
def get_proofreading_test_cases(
    prompt_cls: type[EnglishProofreadingPrompt2] = EnglishProofreadingPrompt2,
) -> list[EnglishProofreadingTestCase2]:
    """Lazily load KOB English proofreading test cases (v2) from JSON."""
    path = test_data_root / title / "core" / "english" / "proofreading.json"
    test_cases = load_test_cases_from_json(path=path, prompt_cls=prompt_cls)

    with open(path, encoding="utf-8") as f:
        raw_test_cases: list[dict] = json.load(f)

    test_cases: list[EnglishProofreadingTestCase2] = []

    for test_case_data in raw_test_cases:
        size = sum(1 for key in test_case_data["query"] if key.startswith("subtitle_"))

        test_case_cls = EnglishProofreadingTestCase2.get_test_case_cls(
            size=size,
            prompt_cls=prompt_cls,
        )
        test_cases.append(test_case_cls.model_validate(test_case_data))

    return test_cases
