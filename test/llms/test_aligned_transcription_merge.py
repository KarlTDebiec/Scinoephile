#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for aligned transcription merge LLM models and processing."""

from __future__ import annotations

import json
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.llms.aligned_transcription_merge import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeManager,
    AlignedTranscriptionMergeProcessor,
    AlignedTranscriptionMergePrompt,
    AlignedTranscriptionMergeQuery,
    AlignedTranscriptionMergeSource,
    AlignedTranscriptionMergeTestCase,
    get_aligned_transcription_merge_support_row,
    get_aligned_transcription_merge_validation,
)
from scinoephile.llms.aligned_transcription_merge.splitting import (
    get_alignment_content_spans,
)

_LOCALIZED_PROMPT = AlignedTranscriptionMergePrompt(
    language=Language.yue_hant,
    sources="laiyuan",
    source_name="mingcheng",
    source_text="yuanwen",
    speaker="shuoshuuren",
    answer_text="wenben",
)
"""Aligned merge prompt with localized correspondence field names."""


def test_alignment_content_spans_exclude_long_pause_separators():
    """Content spans should retain short pauses and exclude long pause runs."""
    shared_pauses = (False, True, False, True, True, True, True, False)

    spans = get_alignment_content_spans(shared_pauses, separator_columns=4)

    assert spans == ((0, 3), (7, 8))


def test_merge_support_row_uses_fullwidth_digits():
    """Source agreement should use portable fullwidth digits."""
    support_row = get_aligned_transcription_merge_support_row(
        ("甲乙・丁", "甲丙・丁"), "甲己・丁", Language.yue_hant
    )

    assert support_row == "９０・９"


def _get_sources(*texts: str) -> list[AlignedTranscriptionMergeSource]:
    """Get named equal-width ASR source rows."""
    return [
        AlignedTranscriptionMergeSource(name=f"source_{index}", text=text)
        for index, text in enumerate(texts, start=1)
    ]


def _get_answer(*texts: str) -> AlignedTranscriptionMergeAnswer:
    """Get one merged answer from subtitle text."""
    return AlignedTranscriptionMergeAnswer(text="".join(text + "｜" for text in texts))


def test_prompt_aliases_are_used_for_nested_llm_correspondence():
    """Generated nested schemas and JSON should use prompt aliases."""
    test_case_cls = AlignedTranscriptionMergeManager.get_test_case_cls(
        _LOCALIZED_PROMPT
    )
    test_case = test_case_cls.model_validate(
        {
            "query": {
                "laiyuan": [
                    {"mingcheng": "one", "yuanwen": "我係"},
                    {"mingcheng": "two", "yuanwen": "我是"},
                ],
                "shuoshuuren": "ＡＡ",
            },
            "answer": {"wenben": "我係｜"},
        }
    )

    assert test_case.query.model_dump(by_alias=True) == {
        "laiyuan": [
            {"mingcheng": "one", "yuanwen": "我係"},
            {"mingcheng": "two", "yuanwen": "我是"},
        ],
        "shuoshuuren": "ＡＡ",
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {"wenben": "我係｜"}


def test_answer_text_derives_ordered_subtitles():
    """Fullwidth boundary markers should deterministically recover subtitles."""
    answer = AlignedTranscriptionMergeAnswer(text="甲乙｜丙丁｜")

    assert answer.transcript == "甲乙丙丁"
    assert [(subtitle.index, subtitle.text) for subtitle in answer.subtitles] == [
        (1, "甲乙"),
        (2, "丙丁"),
    ]


def test_answer_text_can_represent_a_spoken_word_space():
    """Ordinary word spaces should remain part of the consensus transcript."""
    answer = AlignedTranscriptionMergeAnswer(text="Ａ Ｂ｜")

    assert answer.transcript == "Ａ Ｂ"


def test_answer_text_can_omit_a_request_without_consensus():
    """An empty answer should explicitly omit unsupported ASR evidence."""
    answer = AlignedTranscriptionMergeAnswer(text="")

    assert answer.transcript == ""
    assert answer.subtitles == []


def test_answer_text_requires_clean_terminated_subtitles():
    """Answers should terminate every nonblank subtitle and omit input annotations."""
    with raises(ValidationError, match="separated and terminated"):
        AlignedTranscriptionMergeAnswer(text="甲。｜乙！")
    with raises(ValidationError, match="separated and terminated"):
        AlignedTranscriptionMergeAnswer(text="甲。｜｜乙！｜")
    with raises(ValidationError, match="separated and terminated"):
        AlignedTranscriptionMergeAnswer(text="甲・乙｜")


def test_merge_rejects_answer_punctuation():
    """The merger should reject punctuation while its answer model remains tolerant."""
    test_case_cls = AlignedTranscriptionMergeManager.get_test_case_cls(
        _LOCALIZED_PROMPT
    )

    with raises(ValidationError, match="must not contain punctuation"):
        test_case_cls.model_validate(
            {
                "query": {
                    "laiyuan": [
                        {"mingcheng": "one", "yuanwen": "我係"},
                        {"mingcheng": "two", "yuanwen": "我係"},
                    ],
                    "shuoshuuren": "ＡＡ",
                },
                "answer": {"wenben": "我係。｜"},
            }
        )


def test_query_supports_future_sources_and_requires_equal_width_rows():
    """Queries should accept arbitrary ASRs while preserving alignment shape."""
    query_cls = AlignedTranscriptionMergeManager.get_query_cls(
        AlignedTranscriptionMergeManager.base_prompt
    )
    query_data = {
        "sources": [
            {"name": "whisper", "text": "我係"},
            {"name": "mimo", "text": "我是"},
            {"name": "qwen", "text": "我系"},
            {"name": "future", "text": "我係"},
        ],
        "speaker": "ＡＡ",
    }

    query = cast(AlignedTranscriptionMergeQuery, query_cls.model_validate(query_data))

    assert [source.name for source in query.sources] == [
        "whisper",
        "mimo",
        "qwen",
        "future",
    ]
    with raises(ValidationError, match="equal nonzero lengths"):
        query_cls.model_validate({**query_data, "speaker": "Ａ"})


def test_query_accepts_distinct_fullwidth_gap_and_pause_annotations():
    """Queries should distinguish ordinary alignment gaps from timed pauses."""
    query_cls = AlignedTranscriptionMergeManager.get_query_cls(
        AlignedTranscriptionMergeManager.base_prompt
    )
    query = cast(
        AlignedTranscriptionMergeQuery,
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "one", "text": "我　・"},
                    {"name": "two", "text": "我係・"},
                ],
                "speaker": "Ａ　・",
            }
        ),
    )

    assert query.sources[0].text == "我　・"
    assert query.speaker == "Ａ　・"


def test_query_accepts_equal_width_language_singing_and_music_rows():
    """Optional FireRed traces should retain the alignment's exact width."""
    query_cls = AlignedTranscriptionMergeManager.get_query_cls(
        AlignedTranscriptionMergeManager.base_prompt
    )

    query = cast(
        AlignedTranscriptionMergeQuery,
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "one", "text": "甲・乙"},
                    {"name": "two", "text": "甲・乙"},
                ],
                "speaker": "Ａ・Ｂ",
                "language": "粵・日",
                "singing": "唱・　",
                "music": "　・樂",
            }
        ),
    )

    assert query.language_trace == "粵・日"
    assert query.singing_trace == "唱・　"
    assert query.music_trace == "　・樂"


def test_query_rejects_reference_evidence_and_reference_markers():
    """Reference text and diagnostic boundary markers must not reach the LLM."""
    query_cls = AlignedTranscriptionMergeManager.get_query_cls(
        AlignedTranscriptionMergeManager.base_prompt
    )
    with raises(ValidationError, match="reference or guide"):
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "one", "text": "我"},
                    {"name": "reference", "text": "我"},
                ],
                "speaker": "Ａ",
            }
        )
    with raises(ValidationError, match="reference boundary"):
        query_cls.model_validate(
            {
                "sources": [
                    {"name": "one", "text": "我｜"},
                    {"name": "two", "text": "我｜"},
                ],
                "speaker": "Ａ｜",
            }
        )


def test_no_op_answer_selects_first_source_without_annotations():
    """No-op mode should produce one clean first-source subtitle per request."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    processor = AlignedTranscriptionMergeProcessor(
        _LOCALIZED_PROMPT, provider=provider, no_op=True
    )

    answer = processor.process(_get_sources("甲　・乙", "甲丙・乙"), "ＡＡ・Ａ")

    assert answer.transcript == "甲乙"
    provider.chat_completion.assert_not_called()


def test_processor_splits_flat_rows_at_four_shared_pause_characters():
    """Long shared pauses should form separate timing-free merge requests."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "甲｜"}, ensure_ascii=False),
        json.dumps({"wenben": "乙｜"}, ensure_ascii=False),
    ]
    processor = AlignedTranscriptionMergeProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources("甲・・・・乙", "甲・・・・乙"), "Ａ・・・・Ｂ"
    )

    assert [subtitle.text for subtitle in answer.subtitles] == ["甲", "乙"]
    assert [subtitle.index for subtitle in answer.subtitles] == [1, 2]
    assert processor.last_request_spans == ((0, 1), (5, 6))
    assert len(processor.last_request_queries) == 2
    assert [
        query.model_dump(mode="json", by_alias=True)
        for query in processor.last_request_queries
    ] == [
        {
            "laiyuan": [
                {"mingcheng": "source_1", "yuanwen": "甲"},
                {"mingcheng": "source_2", "yuanwen": "甲"},
            ],
            "shuoshuuren": "Ａ",
        },
        {
            "laiyuan": [
                {"mingcheng": "source_1", "yuanwen": "乙"},
                {"mingcheng": "source_2", "yuanwen": "乙"},
            ],
            "shuoshuuren": "Ｂ",
        },
    ]
    assert provider.chat_completion.call_count == 2
    first_messages = provider.chat_completion.call_args_list[0].args[0]
    second_messages = provider.chat_completion.call_args_list[1].args[0]
    assert json.loads(first_messages[1]["content"]) == {
        "laiyuan": [
            {"mingcheng": "source_1", "yuanwen": "甲"},
            {"mingcheng": "source_2", "yuanwen": "甲"},
        ],
        "shuoshuuren": "Ａ",
    }
    assert json.loads(second_messages[1]["content"]) == {
        "laiyuan": [
            {"mingcheng": "source_1", "yuanwen": "乙"},
            {"mingcheng": "source_2", "yuanwen": "乙"},
        ],
        "shuoshuuren": "Ｂ",
    }


def test_processor_omits_one_request_without_discarding_later_consensus():
    """An empty request answer should not discard other request transcripts."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": ""}, ensure_ascii=False),
        json.dumps({"wenben": "乙｜"}, ensure_ascii=False),
    ]
    processor = AlignedTranscriptionMergeProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources("甲・・・・乙", "丙・・・・乙"), "Ａ・・・・Ｂ"
    )

    assert answer.transcript == "乙"
    assert [request.text for request in processor.last_request_answers] == ["", "乙｜"]


def test_processor_retries_subtitles_exceeding_hard_length_limit():
    """Overlong subtitles should receive a specific retry and be split."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "一" * 21 + "｜"}, ensure_ascii=False),
        json.dumps({"wenben": "一" * 11 + "｜" + "一" * 10 + "｜"}, ensure_ascii=False),
    ]
    processor = AlignedTranscriptionMergeProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(_get_sources("一" * 21, "一" * 21), "Ａ" * 21)

    assert [subtitle.text for subtitle in answer.subtitles] == ["一" * 11, "一" * 10]
    retry_messages = provider.chat_completion.call_args.args[0]
    assert "maximum of 20 nonwhitespace characters" in retry_messages[-1]["content"]


def test_processor_retries_answers_omitting_majority_consensus_speech():
    """Answers omitting a large unanimous span should be retried."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "甲乙丙丁｜"}, ensure_ascii=False),
        json.dumps({"wenben": "甲乙丙丁戊己庚辛壬癸｜"}, ensure_ascii=False),
    ]
    processor = AlignedTranscriptionMergeProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))), "Ａ" * 10
    )

    assert answer.transcript == "甲乙丙丁戊己庚辛壬癸"
    retry_messages = provider.chat_completion.call_args.args[0]
    assert "preserves only 40.0%" in retry_messages[-1]["content"]


def test_answer_coverage_allows_locally_supported_character_corrections():
    """The omission guard should allow a minority character at the same column."""
    query = AlignedTranscriptionMergeQuery(
        sources=[
            AlignedTranscriptionMergeSource(name="one", text="盜唔通我唔可以係"),
            AlignedTranscriptionMergeSource(name="two", text="盜唔通我唔可以系"),
            AlignedTranscriptionMergeSource(name="three", text="道唔通我唔可以係"),
        ],
        speaker="ＡＡＡＡＡＡＡＡ",
    )
    answer = AlignedTranscriptionMergeAnswer(text="道唔通我唔可以係｜")

    test_case = AlignedTranscriptionMergeTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_coverage_rejects_equal_length_majority_replacement():
    """Unrelated equal-length text should not count as preserved evidence."""
    query = AlignedTranscriptionMergeQuery(
        sources=_get_sources(*("ＡＢＣＤＥＦＧＨＩＪ" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = AlignedTranscriptionMergeAnswer(text="ＫＬＭＮＯＰＱＲＳＴ｜")

    with raises(ValidationError, match="preserves only 0.0%"):
        AlignedTranscriptionMergeTestCase(query=query, answer=answer)


def test_answer_coverage_rejects_insertions_replacing_missing_majority_span():
    """Inserted text should not compensate for omitted majority characters."""
    query = AlignedTranscriptionMergeQuery(
        sources=_get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = AlignedTranscriptionMergeAnswer(text="甲乙丙丁天地玄黃宇宙｜")

    with raises(ValidationError, match="preserves only 40.0%"):
        AlignedTranscriptionMergeTestCase(query=query, answer=answer)


def test_answer_coverage_accepts_compatibility_width_equivalence():
    """Halfwidth and fullwidth Latin characters should preserve the same evidence."""
    query = AlignedTranscriptionMergeQuery(
        sources=_get_sources(*("June" for _ in range(3))), speaker="Ａ" * 4
    )
    answer = AlignedTranscriptionMergeAnswer(text="Ｊｕｎｅ｜")

    test_case = AlignedTranscriptionMergeTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_coverage_tolerates_one_contextual_spelling_replacement():
    """One mapped unsupported name correction should not fail a short request."""
    query = AlignedTranscriptionMergeQuery(
        sources=_get_sources(*("膠兜依然係咁喺度" for _ in range(3))), speaker="Ａ" * 8
    )
    answer = AlignedTranscriptionMergeAnswer(text="麥兜依然係咁喺度｜")

    test_case = AlignedTranscriptionMergeTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_coverage_does_not_reject_context_resolved_weak_columns():
    """Columns without a strict majority should remain diagnostic rather than fatal."""
    source_texts = ("菇時", "巫師", "　師", "古時", "　時", "姑絲")
    query = AlignedTranscriptionMergeQuery(
        sources=_get_sources(*source_texts), speaker="ＡＡ"
    )
    answer = AlignedTranscriptionMergeAnswer(text="菇時｜")

    validation = get_aligned_transcription_merge_validation(
        source_texts, answer.transcript, Language.yue_hant
    )
    test_case = AlignedTranscriptionMergeTestCase(query=query, answer=answer)

    assert validation.majority_column_count == 0
    assert validation.majority_coverage == 1.0
    assert test_case.answer == answer


def test_empty_answer_requires_absent_majority_evidence():
    """An empty answer should fail only when strict-majority speech is present."""
    weak_query = AlignedTranscriptionMergeQuery(
        sources=_get_sources("甲", "乙", "丙"), speaker="Ａ"
    )
    strong_query = AlignedTranscriptionMergeQuery(
        sources=_get_sources("甲", "甲", "甲"), speaker="Ａ"
    )
    answer = AlignedTranscriptionMergeAnswer(text="")

    assert (
        AlignedTranscriptionMergeTestCase(query=weak_query, answer=answer).answer
        == answer
    )
    with raises(ValidationError, match="preserves only 0.0%"):
        AlignedTranscriptionMergeTestCase(query=strong_query, answer=answer)
