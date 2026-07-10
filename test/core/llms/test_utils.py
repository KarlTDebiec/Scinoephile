#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM test-case JSON utilities."""

from __future__ import annotations

import json
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.llms.review import ReviewManager, ReviewPrompt

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt.from_attributes(
    Language.zho_hans,
    {
        "input_pfx": "zimu_",
        "output_pfx": "xiugai_",
        "note_pfx": "beizhu_",
    },
)
"""Review prompt using localized correspondence field names."""


def test_json_uses_base_prompt_fields(tmp_path: Path):
    """JSON should persist base fields and load them into a concrete prompt."""
    test_case_cls = ReviewManager.get_test_case_cls(1, _LOCALIZED_REVIEW_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {"zimu_1": "original"},
            "answer": {"xiugai_1": "corrected", "beizhu_1": "typo"},
            "verified": True,
        }
    )
    output_path = tmp_path / "test_cases.json"

    save_test_cases_to_json(output_path, [test_case], ReviewManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"subtitle_1": "original"},
            "answer": {"revised_1": "corrected", "note_1": "typo"},
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        ReviewManager,
        _LOCALIZED_REVIEW_PROMPT,
    )
    assert loaded[0].query.model_dump() == {"zimu_1": "original"}
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump() == {
        "xiugai_1": "corrected",
        "beizhu_1": "typo",
    }
