#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM test-case JSON utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

from pydantic import ValidationError
from pytest import mark, raises

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


def _get_test_case(original: str, corrected: str):
    """Build an aliased review test case.

    Arguments:
        original: original subtitle text
        corrected: corrected subtitle text
    Returns:
        review test case
    """
    test_case_cls = _AliasedBaseReviewManager.get_test_case_cls(
        _LOCALIZED_REVIEW_PROMPT
    )
    return test_case_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": original}]},
            "answer": {
                "revisions": [
                    {
                        "index": 1,
                        "text": corrected,
                        "note": "typo",
                    }
                ]
            },
        }
    )


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


@mark.parametrize(
    "test_case_data",
    [
        {"query": {"subtitles": [{"index": 1, "text": "original"}]}},
        {"query": {"zimu": [{"xuhao": 1, "wenben": "original"}]}},
        {
            "query": {
                "base_subtitles": [
                    {
                        "base_index": 1,
                        "base_text": "original",
                        "unexpected": True,
                    }
                ]
            }
        },
        {
            "query": {
                "base_subtitles": [{"base_index": 1, "base_text": "original"}],
                "unexpected": True,
            }
        },
        {
            "query": {"base_subtitles": [{"base_index": 1, "base_text": "original"}]},
            "unexpected": True,
        },
    ],
    ids=[
        "semantic-fields",
        "localized-fields",
        "unknown-subtitle-field",
        "unknown-query-field",
        "unknown-test-case-field",
    ],
)
def test_json_loading_rejects_non_base_fields(
    tmp_path: Path,
    test_case_data: dict,
):
    """Repository JSON should contain only base prompt aliases."""
    input_path = tmp_path / "test_cases.json"
    input_path.write_text(
        json.dumps([test_case_data], ensure_ascii=False),
        encoding="utf-8",
    )

    with raises(ValidationError):
        load_test_cases_from_json(
            input_path,
            _AliasedBaseReviewManager,
            _LOCALIZED_REVIEW_PROMPT,
        )


@mark.parametrize(
    "test_case_data",
    [
        {"query": []},
        {"query": {"base_subtitles": "not a list"}},
        {"query": {"base_subtitles": [{"base_index": "1", "base_text": "original"}]}},
    ],
    ids=["non-object-query", "non-list-subtitles", "coerced-index"],
)
def test_json_loading_is_strict(tmp_path: Path, test_case_data: dict):
    """Repository JSON should reject values requiring type coercion."""
    input_path = tmp_path / "test_cases.json"
    input_path.write_text(json.dumps([test_case_data]), encoding="utf-8")

    with raises(ValidationError):
        load_test_cases_from_json(
            input_path,
            _AliasedBaseReviewManager,
            _LOCALIZED_REVIEW_PROMPT,
        )


@mark.parametrize("contents", [{}, ["not an object"]])
def test_json_loading_requires_an_array_of_objects(tmp_path: Path, contents: object):
    """Repository test-case files should contain an array of objects."""
    input_path = tmp_path / "test_cases.json"
    input_path.write_text(json.dumps(contents), encoding="utf-8")

    with raises(ValidationError):
        load_test_cases_from_json(
            input_path,
            _AliasedBaseReviewManager,
            _LOCALIZED_REVIEW_PROMPT,
        )


def test_save_preserves_existing_cases_unless_pruning(tmp_path: Path):
    """Saving a partial run should retain unencountered persisted cases."""
    output_path = tmp_path / "test_cases.json"
    existing_test_case = _get_test_case("existing", "existing corrected")
    encountered_test_case = _get_test_case("encountered", "encountered corrected")
    save_test_cases_to_json(
        output_path,
        [existing_test_case],
        _AliasedBaseReviewManager,
    )

    save_test_cases_to_json(
        output_path,
        [encountered_test_case],
        _AliasedBaseReviewManager,
    )

    loaded = load_test_cases_from_json(
        output_path,
        _AliasedBaseReviewManager,
        _LOCALIZED_REVIEW_PROMPT,
    )
    assert [
        test_case.query.model_dump()["subtitles"][0]["text"] for test_case in loaded
    ] == [
        "existing",
        "encountered",
    ]

    save_test_cases_to_json(
        output_path,
        [encountered_test_case],
        _AliasedBaseReviewManager,
        prune=True,
    )

    loaded = load_test_cases_from_json(
        output_path,
        _AliasedBaseReviewManager,
        _LOCALIZED_REVIEW_PROMPT,
    )
    assert [
        test_case.query.model_dump()["subtitles"][0]["text"] for test_case in loaded
    ] == ["encountered"]


def test_save_replaces_existing_file_atomically(tmp_path: Path):
    """A failed save should leave the existing file unchanged."""
    output_path = tmp_path / "test_cases.json"
    save_test_cases_to_json(
        output_path,
        [_get_test_case("existing", "existing corrected")],
        _AliasedBaseReviewManager,
    )
    original_contents = output_path.read_bytes()

    with (
        patch(
            "scinoephile.core.llms.utils.json.dump",
            side_effect=OSError("write failed"),
        ),
        raises(OSError, match="write failed"),
    ):
        save_test_cases_to_json(
            output_path,
            [_get_test_case("new", "new corrected")],
            _AliasedBaseReviewManager,
        )

    assert output_path.read_bytes() == original_contents
    assert list(tmp_path.glob(".test_cases.json.*.tmp")) == []
