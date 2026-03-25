#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Queryer tool-related behavior."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.llms.base import Answer, Prompt, Query, Queryer, TestCase


class _Prompt(Prompt):
    """Minimal prompt for Queryer tests."""

    base_system_prompt: ClassVar[str] = "system"
    schema_intro: ClassVar[str] = "schema"
    few_shot_intro: ClassVar[str] = "few shot"
    few_shot_query_intro: ClassVar[str] = "query"
    few_shot_answer_intro: ClassVar[str] = "answer"
    answer_invalid_pre: ClassVar[str] = "invalid answer"
    answer_invalid_post: ClassVar[str] = "end invalid answer"
    test_case_invalid_pre: ClassVar[str] = "invalid test case"
    test_case_invalid_post: ClassVar[str] = "end invalid test case"


class _Query(Query):
    """Minimal query model for Queryer tests."""

    prompt_cls = _Prompt
    source: str


class _Answer(Answer):
    """Minimal answer model for Queryer tests."""

    prompt_cls = _Prompt
    output: str


class _TestCase(TestCase):
    """Minimal test case model for Queryer tests."""

    prompt_cls = _Prompt
    query_cls = _Query
    answer_cls = _Answer
    query: _Query
    answer: _Answer | None = None


def test_cache_path_changes_when_tools_change(tmp_path):
    """Test cache key incorporates configured tools and handlers."""
    queryer_cls = Queryer.get_queryer_cls(_Prompt)
    queryer = queryer_cls(cache_dir_path=str(tmp_path))

    system_prompt = queryer._get_system_prompt(_Answer)
    query_prompt = '{"source": "value"}'

    without_tools_path = queryer._get_cache_path(system_prompt, "", query_prompt)
    with_tools_path = queryer._get_cache_path(
        system_prompt,
        '{"handler_names":["lookup_dictionary"],"tools":[]}',
        query_prompt,
    )

    assert without_tools_path is not None
    assert with_tools_path is not None
    assert without_tools_path != with_tools_path


def test_tools_json_uses_tool_specs_and_handler_names():
    """Test tools JSON is stable for configured tool metadata."""
    queryer_cls = Queryer.get_queryer_cls(_Prompt)
    queryer = queryer_cls(
        tools=[
            {
                "name": "lookup_dictionary",
                "description": "Lookup dictionary entries.",
                "parameters": {"type": "object"},
            }
        ],
        tool_handlers={
            "lookup_dictionary": lambda arguments: arguments,
            "other_tool": lambda arguments: arguments,
        },
    )

    tools_json = queryer._get_tools_json()

    assert '"name": "lookup_dictionary"' in tools_json
    assert '"handler_names": ["lookup_dictionary", "other_tool"]' in tools_json
