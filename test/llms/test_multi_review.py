#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for multi-source review LLM models and processing."""

from __future__ import annotations

import json
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.multi_review import (
    MultiReviewManager,
    MultiReviewProcessor,
    MultiReviewPrompt,
    MultiReviewTestCase,
)

_LOCALIZED_PROMPT = MultiReviewPrompt(
    language=Language.yue_hant,
    sources="laiyuan",
    guides="zhongwen",
    outputs="shuchu",
    source_name="mingcheng",
    subtitles="zhuanxie",
    index="xuhao",
    text="wenben",
)
"""Multi-review prompt with localized correspondence field names."""

_BOUNDARY_AWARE_PROMPT = MultiReviewPrompt(boundary_aware=True)
"""Multi-review prompt that reconciles provisional boundaries across a block."""


def test_prompt_aliases_are_used_for_nested_llm_correspondence():
    """Generated nested schemas and JSON should use prompt-specific aliases."""
    test_case_cls = MultiReviewManager.get_test_case_cls(_LOCALIZED_PROMPT)
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "laiyuan": [
                    {
                        "mingcheng": "one",
                        "zhuanxie": [{"xuhao": 1, "wenben": "來源一"}],
                    },
                    {
                        "mingcheng": "two",
                        "zhuanxie": [{"xuhao": 1, "wenben": "來源二"}],
                    },
                ],
                "zhongwen": [{"xuhao": 1, "wenben": "指引"}],
            },
            "answer": {"shuchu": [{"xuhao": 1, "wenben": "輸出"}]},
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "laiyuan": [
            {"mingcheng": "one", "zhuanxie": [{"xuhao": 1, "wenben": "來源一"}]},
            {"mingcheng": "two", "zhuanxie": [{"xuhao": 1, "wenben": "來源二"}]},
        ],
        "zhongwen": [{"xuhao": 1, "wenben": "指引"}],
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "shuchu": [{"xuhao": 1, "wenben": "輸出"}]
    }


def test_query_requires_unique_sources_and_guide_aligned_ordered_indexes():
    """Sources should be unique and their sparse indexes should align to guides."""
    query_cls = MultiReviewManager.get_query_cls(MultiReviewManager.base_prompt)
    guides = [{"index": 1, "text": "one"}, {"index": 2, "text": "two"}]

    with raises(ValidationError, match="at least 2 items"):
        query_cls.model_validate(
            {"sources": [{"name": "one", "subtitles": []}], "guides": guides}
        )
    with raises(ValidationError, match="nonblank and unique"):
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "same", "subtitles": []},
                    {"name": " same ", "subtitles": []},
                ],
                "guides": guides,
            }
        )
    with raises(ValidationError, match="unique and in ascending order"):
        query_cls.model_validate(
            {
                "sources": [
                    {
                        "name": "one",
                        "subtitles": [
                            {"index": 2, "text": "two"},
                            {"index": 1, "text": "one"},
                        ],
                    },
                    {"name": "two", "subtitles": []},
                ],
                "guides": guides,
            }
        )
    with raises(ValidationError, match="correspond to a guide index"):
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "one", "subtitles": [{"index": 3, "text": "three"}]},
                    {"name": "two", "subtitles": []},
                ],
                "guides": guides,
            }
        )


def test_answer_must_cover_every_guide_and_leave_unsupported_positions_blank():
    """Answers should be complete but may not synthesize unsupported text."""
    query = {
        "sources": [
            {"name": "one", "subtitles": [{"index": 1, "text": "source"}]},
            {"name": "two", "subtitles": []},
        ],
        "guides": [
            {"index": 1, "text": "guide one"},
            {"index": 2, "text": "guide two"},
        ],
    }

    with raises(ValidationError, match="correspond exactly"):
        MultiReviewTestCase.model_validate(
            {"query": query, "answer": {"outputs": [{"index": 1, "text": "output"}]}}
        )
    with raises(ValidationError, match="must be blank"):
        MultiReviewTestCase.model_validate(
            {
                "query": query,
                "answer": {
                    "outputs": [
                        {"index": 1, "text": "output"},
                        {"index": 2, "text": "translated guide"},
                    ]
                },
            }
        )

    test_case = MultiReviewTestCase.model_validate(
        {
            "query": query,
            "answer": {
                "outputs": [{"index": 1, "text": "output"}, {"index": 2, "text": ""}]
            },
        }
    )
    assert test_case.answer is not None


def test_boundary_aware_answer_rejects_conflicting_fragment_duplication():
    """Block-global answers should not combine whole and split source variants."""
    query = {
        "sources": [
            {"name": "whole", "subtitles": [{"index": 1, "text": "完整句子後半段落"}]},
            {
                "name": "split",
                "subtitles": [
                    {"index": 1, "text": "完整句子"},
                    {"index": 2, "text": "後半段落"},
                ],
            },
        ],
        "guides": [{"index": 1, "text": "第一句"}, {"index": 2, "text": "第二句"}],
    }
    answer = {
        "outputs": [
            {"index": 1, "text": "完整句子後半段落"},
            {"index": 2, "text": "後半段落"},
        ]
    }

    boundary_aware_cls = MultiReviewManager.get_test_case_cls(_BOUNDARY_AWARE_PROMPT)
    with raises(ValidationError, match="whole-versus-split"):
        boundary_aware_cls.model_validate({"query": query, "answer": answer})

    standard = MultiReviewTestCase.model_validate({"query": query, "answer": answer})
    assert standard.answer is not None


def test_boundary_aware_answer_can_move_text_to_an_unsupported_index():
    """Block-global review may move misplaced source text to an adjacent blank."""
    test_case_cls = MultiReviewManager.get_test_case_cls(_BOUNDARY_AWARE_PROMPT)

    test_case = test_case_cls.model_validate(
        {
            "query": {
                "sources": [
                    {"name": "one", "subtitles": [{"index": 1, "text": "移去下一行"}]},
                    {"name": "two", "subtitles": [{"index": 1, "text": "移去下一行"}]},
                ],
                "guides": [
                    {"index": 1, "text": "第一句"},
                    {"index": 2, "text": "下一句"},
                ],
            },
            "answer": {
                "outputs": [
                    {"index": 1, "text": ""},
                    {"index": 2, "text": "移去下一行"},
                ]
            },
        }
    )

    assert test_case.answer is not None


def test_boundary_aware_answer_rejects_distant_text_without_local_support():
    """Block-global review should not move source text beyond direct neighbors."""
    test_case_cls = MultiReviewManager.get_test_case_cls(_BOUNDARY_AWARE_PROMPT)

    with raises(ValidationError, match="output 1 must be blank"):
        test_case_cls.model_validate(
            {
                "query": {
                    "sources": [
                        {
                            "name": "one",
                            "subtitles": [{"index": 3, "text": "重複對白片段"}],
                        },
                        {
                            "name": "two",
                            "subtitles": [{"index": 3, "text": "重複對白片段"}],
                        },
                    ],
                    "guides": [
                        {"index": 1, "text": "第一句"},
                        {"index": 2, "text": "第二句"},
                        {"index": 3, "text": "第三句"},
                    ],
                },
                "answer": {
                    "outputs": [
                        {"index": 1, "text": "重複對白片段"},
                        {"index": 2, "text": ""},
                        {"index": 3, "text": "重複對白片段"},
                    ]
                },
            }
        )


def test_boundary_aware_answer_allows_supported_single_character_correction():
    """A one-character ASR correction may rely on nearby nonempty evidence."""
    test_case_cls = MultiReviewManager.get_test_case_cls(_BOUNDARY_AWARE_PROMPT)

    test_case = test_case_cls.model_validate(
        {
            "query": {
                "sources": [
                    {"name": "one", "subtitles": [{"index": 1, "text": "哇"}]},
                    {"name": "two", "subtitles": [{"index": 1, "text": "哇"}]},
                ],
                "guides": [{"index": 1, "text": "嘩！"}],
            },
            "answer": {"outputs": [{"index": 1, "text": "嘩！"}]},
        }
    )

    assert test_case.answer is not None


def test_processor_uses_sparse_sources_and_guide_timing():
    """Processor should query sparse inputs and return complete guide-timed output."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    provider.chat_completion.return_value = json.dumps(
        {
            "shuchu": [
                {"xuhao": 1, "wenben": "綜合一"},
                {"xuhao": 2, "wenben": "綜合二"},
            ]
        },
        ensure_ascii=False,
    )
    processor = MultiReviewProcessor(_LOCALIZED_PROMPT, provider=provider)
    sources = {
        "one": Series(events=[Subtitle(start=0, end=1000, text="來源一")]),
        "two": Series(events=[Subtitle(start=1100, end=2000, text="來源二")]),
    }
    guide = Series(
        events=[
            Subtitle(start=0, end=1000, text="指引一"),
            Subtitle(start=1100, end=2000, text="指引二"),
        ]
    )

    output = processor.process(sources, guide)

    assert [(subtitle.start, subtitle.end, subtitle.text) for subtitle in output] == [
        (0, 1000, "綜合一"),
        (1100, 2000, "綜合二"),
    ]
    messages = provider.chat_completion.call_args.args[0]
    assert json.loads(messages[1]["content"]) == {
        "laiyuan": [
            {"mingcheng": "one", "zhuanxie": [{"xuhao": 1, "wenben": "來源一"}]},
            {"mingcheng": "two", "zhuanxie": [{"xuhao": 2, "wenben": "來源二"}]},
        ],
        "zhongwen": [
            {"xuhao": 1, "wenben": "指引一"},
            {"xuhao": 2, "wenben": "指引二"},
        ],
    }


def test_processor_rejects_source_timing_absent_from_guide():
    """Source cues should align exactly to guide cue timing."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    processor = MultiReviewProcessor(_LOCALIZED_PROMPT, provider=provider)
    sources = {
        "one": Series(events=[Subtitle(start=0, end=900, text="one")]),
        "two": Series(events=[Subtitle(start=0, end=1000, text="two")]),
    }
    guide = Series(events=[Subtitle(start=0, end=1000, text="guide")])

    with raises(ScinoephileError, match="absent from the guide"):
        processor.process(sources, guide)
