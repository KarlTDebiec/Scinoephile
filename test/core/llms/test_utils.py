#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM test-case JSON utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from scinoephile.core import Language
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)
from scinoephile.llms.review import ReviewManager, ReviewPrompt

_BASE_REVIEW_PROMPT = ReviewPrompt(
    subtitles="base_subtitles",
    revisions="base_revisions",
    index="base_index",
    text="base_text",
    note="base_note",
)
"""Review prompt whose aliases intentionally differ from semantic field names."""

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt(
    language=Language.zho_hans,
    subtitles="zimu",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
)
"""Review prompt using localized correspondence field names."""


class _AliasedBaseReviewManager(ReviewManager):
    """Review manager with distinct semantic, base, and localized field names."""

    operation: ClassVar[str] = "aliased-base-review"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[ReviewPrompt] = _BASE_REVIEW_PROMPT
    """Prompt defining intentionally distinct persisted field names."""


def test_json_uses_base_prompt_fields(tmp_path: Path):
    """JSON should persist base fields and load them into a concrete prompt."""
    test_case_cls = _AliasedBaseReviewManager.get_test_case_cls(
        _LOCALIZED_REVIEW_PROMPT
    )
    test_case = test_case_cls.model_validate(
        {
            "query": {"zimu": [{"xuhao": 1, "wenben": "original"}]},
            "answer": {
                "xiugai": [
                    {
                        "xuhao": 1,
                        "wenben": "corrected",
                        "beizhu": "typo",
                    }
                ]
            },
            "verified": True,
        }
    )
    output_path = tmp_path / "test_cases.json"

    save_test_cases_to_json(output_path, [test_case], _AliasedBaseReviewManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"base_subtitles": [{"base_index": 1, "base_text": "original"}]},
            "answer": {
                "base_revisions": [
                    {
                        "base_index": 1,
                        "base_text": "corrected",
                        "base_note": "typo",
                    }
                ]
            },
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        _AliasedBaseReviewManager,
        _LOCALIZED_REVIEW_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "original"}]
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "corrected", "beizhu": "typo"}]
    }
