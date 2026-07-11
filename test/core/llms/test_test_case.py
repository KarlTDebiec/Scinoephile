#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the core LLM test-case model."""

from __future__ import annotations

from scinoephile.core.llms import Answer, Prompt, Query, TestCase

_PROMPT = Prompt()
"""Prompt fixture for core test-case models."""


class _Query(Query):
    """Query fixture for core test-case models."""

    text: str
    """Query text."""


class _Answer(Answer):
    """Answer fixture for core test-case models."""

    text: str
    """Answer text."""


class _TestCase(TestCase):
    """Test-case fixture with a nonzero minimum difficulty."""

    query: _Query
    """Query fixture."""
    answer: _Answer | None = None
    """Optional answer fixture."""

    def get_min_difficulty(self) -> int:
        """Get the fixture's minimum difficulty.

        Returns:
            minimum difficulty
        """
        return 2


_Query.prompt = _PROMPT
_Answer.prompt = _PROMPT
_TestCase.query_cls = _Query
_TestCase.answer_cls = _Answer
_TestCase.prompt = _PROMPT


def test_test_case_enforces_minimum_difficulty_without_lowering_higher_values():
    """Validation should floor difficulty without lowering an explicit value."""
    minimum = _TestCase.model_validate({"query": {"text": "query"}, "difficulty": 0})
    higher = _TestCase.model_validate({"query": {"text": "query"}, "difficulty": 3})

    assert minimum.difficulty == 2
    assert higher.difficulty == 3


def test_test_case_metadata_fields_have_stable_schema():
    """Test-case metadata should have stable order, defaults, and descriptions."""
    schema = _TestCase.model_json_schema()

    assert list(schema["properties"]) == [
        "query",
        "answer",
        "difficulty",
        "few_shot",
        "verified",
    ]
    assert schema["properties"]["difficulty"] == {
        "default": 0,
        "description": "Difficulty level of the test case, used for filtering.",
        "title": "Difficulty",
        "type": "integer",
    }
    assert schema["properties"]["few_shot"] == {
        "default": False,
        "description": "Whether to include test case in few-shot examples.",
        "title": "Few Shot",
        "type": "boolean",
    }
    assert schema["properties"]["verified"] == {
        "default": False,
        "description": "Whether to include test case in the verified answers cache.",
        "title": "Verified",
        "type": "boolean",
    }
