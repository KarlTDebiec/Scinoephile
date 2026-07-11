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

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt(
    language=Language.zho_hans,
    subtitles="zimu",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
)
"""Review prompt using localized correspondence field names."""


def test_json_uses_base_prompt_fields(tmp_path: Path):
    """JSON should persist base fields and load them into a concrete prompt."""
    test_case_cls = ReviewManager.get_test_case_cls(_LOCALIZED_REVIEW_PROMPT)
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

    save_test_cases_to_json(output_path, [test_case], ReviewManager)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {
            "query": {"subtitles": [{"index": 1, "text": "original"}]},
            "answer": {
                "revisions": [{"index": 1, "text": "corrected", "note": "typo"}]
            },
            "difficulty": 1,
            "verified": True,
        }
    ]
    loaded = load_test_cases_from_json(
        output_path,
        ReviewManager,
        _LOCALIZED_REVIEW_PROMPT,
    )
    assert loaded[0].query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "original"}]
    }
    assert loaded[0].answer is not None
    assert loaded[0].answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "corrected", "beizhu": "typo"}]
    }
