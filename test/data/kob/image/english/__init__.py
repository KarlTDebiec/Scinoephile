#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from typing import cast

from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.image.english.fusion import (
    EnglishFusionPrompt2,
    EnglishFusionTestCase2,
)
from scinoephile.testing import test_data_root

title = "kob"


@cache
def get_fusion_test_cases(
    prompt_cls: type[EnglishFusionPrompt2] = EnglishFusionPrompt2,
) -> list[EnglishFusionTestCase2]:
    """Load English fusion test cases from JSON.

    Arguments:
        prompt_cls: text strings to be used for corresponding with LLM
    Returns:
        list of English fusion test cases
    """
    path = test_data_root / title / "image" / "english" / "fusion.json"
    test_cases = load_test_cases_from_json(
        path, EnglishFusionTestCase2, prompt_cls=prompt_cls
    )
    return cast(list[EnglishFusionTestCase2], test_cases)
