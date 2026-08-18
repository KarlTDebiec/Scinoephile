#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transcription LLM models and processing."""

from __future__ import annotations

import json
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import LogCaptureFixture, raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionAnswer,
    TranscriptionManager,
    TranscriptionProcessor,
    TranscriptionPrompt,
    TranscriptionQuery,
    TranscriptionSource,
    TranscriptionTestCase,
)

_LOCALIZED_PROMPT = TranscriptionPrompt(
    language=Language.yue_hant,
    sources="laiyuan",
    source_name="mingcheng",
    source_text="yuanwen",
    speaker="shuoshuuren",
    answer_text="wenben",
)
"""Transcription prompt with localized correspondence field names."""


def _get_sources(*texts: str) -> list[TranscriptionSource]:
    """Get named equal-width ASR source rows."""
    return [
        TranscriptionSource(name=f"source_{index}", text=text)
        for index, text in enumerate(texts, start=1)
    ]


def _get_answer(*texts: str) -> TranscriptionAnswer:
    """Get one consensus answer from subtitle text."""
    return TranscriptionAnswer(text="".join(text + "｜" for text in texts))


def test_prompt_aliases_are_used_for_nested_llm_correspondence():
    """Generated nested schemas and JSON should use prompt aliases."""
    test_case_cls = TranscriptionManager.get_test_case_cls(_LOCALIZED_PROMPT)
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
    answer = TranscriptionAnswer(text="甲乙｜丙丁｜")

    assert answer.transcript == "甲乙丙丁"
    assert [(subtitle.index, subtitle.text) for subtitle in answer.subtitles] == [
        (1, "甲乙"),
        (2, "丙丁"),
    ]


def test_answer_text_can_represent_a_spoken_word_space():
    """Ordinary word spaces should remain part of the consensus transcript."""
    answer = TranscriptionAnswer(text="Ａ Ｂ｜")

    assert answer.transcript == "Ａ Ｂ"


def test_answer_text_can_omit_a_request_without_consensus():
    """An empty answer should explicitly omit unsupported ASR evidence."""
    answer = TranscriptionAnswer(text="")

    assert answer.transcript == ""
    assert answer.subtitles == []


def test_answer_text_requires_clean_terminated_subtitles():
    """Answers should terminate every nonblank subtitle and omit input annotations."""
    with raises(ValidationError, match="separated and terminated"):
        TranscriptionAnswer(text="甲。｜乙！")
    with raises(ValidationError, match="separated and terminated"):
        TranscriptionAnswer(text="甲。｜｜乙！｜")
    with raises(ValidationError, match="separated and terminated"):
        TranscriptionAnswer(text="甲・乙｜")


def test_answer_rejects_punctuation():
    """Answer validation should reject punctuation."""
    answer_cls = TranscriptionManager.get_answer_cls(_LOCALIZED_PROMPT)

    with raises(ValidationError, match="must not contain punctuation"):
        answer_cls.model_validate({"wenben": "我係。｜"})


def test_answer_rejects_overlong_subtitles():
    """Answer validation should reject overlong display subtitles."""
    with raises(ValidationError, match="maximum of 20 nonwhitespace characters"):
        TranscriptionAnswer(text="一" * 21 + "｜")


def test_query_supports_future_sources_and_requires_equal_width_rows():
    """Queries should accept arbitrary ASRs while preserving alignment shape."""
    query_cls = TranscriptionManager.get_query_cls(TranscriptionManager.base_prompt)
    query_data = {
        "sources": [
            {"name": "whisper", "text": "我係"},
            {"name": "mimo", "text": "我是"},
            {"name": "qwen", "text": "我系"},
            {"name": "future", "text": "我係"},
        ],
        "speaker": "ＡＡ",
    }

    query = cast(TranscriptionQuery, query_cls.model_validate(query_data))

    assert [source.name for source in query.sources] == [
        "whisper",
        "mimo",
        "qwen",
        "future",
    ]
    with raises(ValidationError, match="equal nonzero lengths"):
        query_cls.model_validate({**query_data, "speaker": "Ａ"})


def test_query_strips_source_names_before_checking_uniqueness():
    """Source names should be normalized before storage and comparison."""
    query = TranscriptionQuery(
        sources=[TranscriptionSource(name=" one ", text="甲")], speaker="Ａ"
    )

    assert query.sources[0].name == "one"

    with raises(ValidationError, match="nonblank and unique"):
        TranscriptionQuery(
            sources=[
                TranscriptionSource(name="one", text="甲"),
                TranscriptionSource(name=" one ", text="甲"),
            ],
            speaker="Ａ",
        )


def test_query_supports_one_source():
    """A single ASR row should be sufficient for transcription."""
    query = TranscriptionQuery(sources=_get_sources("我係"), speaker="ＡＡ")

    assert [source.text for source in query.sources] == ["我係"]


def test_query_accepts_distinct_fullwidth_gap_and_pause_annotations():
    """Queries should distinguish ordinary alignment gaps from timed pauses."""
    query_cls = TranscriptionManager.get_query_cls(TranscriptionManager.base_prompt)
    query = cast(
        TranscriptionQuery,
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


def test_query_rejects_audit_only_analysis_rows():
    """Language and audio-event traces should not enter LLM correspondence."""
    query_cls = TranscriptionManager.get_query_cls(TranscriptionManager.base_prompt)

    with raises(ValidationError, match="Extra inputs are not permitted"):
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
        )


def test_query_rejects_reference_evidence_and_reference_markers():
    """Reference text and diagnostic boundary markers must not reach the LLM."""
    query_cls = TranscriptionManager.get_query_cls(TranscriptionManager.base_prompt)
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


def test_processor_no_op_uses_column_plurality_consensus():
    """No-op mode should select each column's plurality without an LLM."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider, no_op=True)

    answer = processor.process(_get_sources("甲　・乙", "甲丙・乙"), "ＡＡ・Ａ")

    assert answer.text == "甲乙｜"
    provider.chat_completion.assert_not_called()


def test_processor_no_op_preserves_request_spans_and_subtitle_limits():
    """No-op requests should retain spans and split overlong consensus text."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider, no_op=True)
    source_text = f"{'一' * 21}・・・・乙"
    speaker = f"{'Ａ' * 21}・・・・Ｂ"

    results = processor.process_requests(
        _get_sources(source_text, source_text), speaker
    )

    assert [
        (
            result.start_column,
            result.end_column,
            [subtitle.text for subtitle in result.answer.subtitles],
        )
        for result in results
    ] == [(0, 21, ["一" * 20, "一"]), (25, 26, ["乙"])]
    provider.chat_completion.assert_not_called()


def test_processor_transcribes_one_source():
    """One ASR source should be sent through the normal transcription path."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps(
        {"wenben": "我係｜"}, ensure_ascii=False
    )
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(_get_sources("我係"), "ＡＡ")

    assert answer.transcript == "我係"
    provider.chat_completion.assert_called_once()


def test_processor_splits_flat_rows_at_four_shared_pause_characters():
    """Long shared pauses should form separate timing-free requests."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "甲｜"}, ensure_ascii=False),
        json.dumps({"wenben": "乙｜"}, ensure_ascii=False),
    ]
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources("甲・・・・乙", "甲・・・・乙"), "Ａ・・・・Ｂ"
    )

    assert [subtitle.text for subtitle in answer.subtitles] == ["甲", "乙"]
    assert [subtitle.index for subtitle in answer.subtitles] == [1, 2]
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


def test_processor_does_not_split_at_discontinuous_timed_pauses():
    """Adjacent rendered pauses should split only when temporally continuous."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps(
        {"wenben": "甲乙｜"}, ensure_ascii=False
    )
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    results = processor.process_requests(
        _get_sources("甲・・・・乙", "甲・・・・乙"),
        "Ａ・・・・Ｂ",
        pause_intervals_seconds=(
            None,
            (1.0, 1.473),
            (1.996, 2.246),
            (2.246, 2.496),
            (2.496, 2.857),
            None,
        ),
    )

    assert [
        (result.start_column, result.end_column, result.answer.transcript)
        for result in results
    ] == [(0, 6, "甲乙")]
    provider.chat_completion.assert_called_once()


def test_processor_splits_at_continuous_timed_pause():
    """A continuous one-second timed pause should divide requests."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "甲｜"}, ensure_ascii=False),
        json.dumps({"wenben": "乙｜"}, ensure_ascii=False),
    ]
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    results = processor.process_requests(
        _get_sources("甲・・・・乙", "甲・・・・乙"),
        "Ａ・・・・Ｂ",
        pause_intervals_seconds=(
            None,
            (1.0, 1.25),
            (1.25, 1.5),
            (1.5, 1.75),
            (1.75, 2.0),
            None,
        ),
    )

    assert [
        (result.start_column, result.end_column, result.answer.transcript)
        for result in results
    ] == [(0, 1, "甲"), (5, 6, "乙")]
    assert provider.chat_completion.call_count == 2


def test_processor_exposes_request_alignment_spans():
    """Request results should retain their complete-alignment column spans."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"wenben": "甲｜"}, ensure_ascii=False),
        json.dumps({"wenben": "乙｜"}, ensure_ascii=False),
    ]
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    results = processor.process_requests(
        _get_sources("甲・・・・乙", "甲・・・・乙"), "Ａ・・・・Ｂ"
    )

    assert [
        (result.start_column, result.end_column, result.answer.transcript)
        for result in results
    ] == [(0, 1, "甲"), (5, 6, "乙")]
    assert [result.query_key_sha256 for result in results] == [
        call.kwargs["query_key_sha256"]
        for call in provider.chat_completion.call_args_list
    ]


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
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources("甲・・・・乙", "丙・・・・乙"), "Ａ・・・・Ｂ"
    )

    assert answer.transcript == "乙"
    assert provider.chat_completion.call_count == 2


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
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(_get_sources("一" * 21, "一" * 21), "Ａ" * 21)

    assert [subtitle.text for subtitle in answer.subtitles] == ["一" * 11, "一" * 10]
    retry_messages = provider.chat_completion.call_args.args[0]
    assert "maximum of 20 nonwhitespace characters" in retry_messages[-1]["content"]


def test_processor_retries_answers_omitting_strong_consensus_speech():
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
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))), "Ａ" * 10
    )

    assert answer.transcript == "甲乙丙丁戊己庚辛壬癸"
    retry_messages = provider.chat_completion.call_args.args[0]
    assert "6 consecutive" in retry_messages[-1]["content"]
    assert "戊己庚辛壬癸" in retry_messages[-1]["content"]


def test_processor_falls_back_after_invalid_consensus_retries(
    caplog: LogCaptureFixture,
):
    """Exhausted retries should use and accurately log deterministic consensus.

    Arguments:
        caplog: captured log records
    """
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps(
        {"wenben": "甲｜"}, ensure_ascii=False
    )
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)
    source_text = "甲乙丙丁戊己庚辛壬癸"

    answer = processor.process(
        _get_sources(*(source_text for _ in range(3))), "Ａ" * len(source_text)
    )

    assert answer.transcript == source_text
    assert provider.chat_completion.call_count == 5
    assert f"used deterministic column consensus: {source_text + '｜'!r}" in caplog.text


def test_answer_consensus_allows_pronunciation_supported_corrections():
    """The omission guard should allow a minority character at the same column."""
    query = TranscriptionQuery(
        sources=[
            TranscriptionSource(name="one", text="盜唔通我唔可以係"),
            TranscriptionSource(name="two", text="盜唔通我唔可以系"),
            TranscriptionSource(name="three", text="道唔通我唔可以係"),
        ],
        speaker="ＡＡＡＡＡＡＡＡ",
    )
    answer = TranscriptionAnswer(text="道唔通我唔可以係｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_consensus_rejects_equal_length_majority_replacement():
    """Unrelated equal-length text should not count as preserved evidence."""
    query = TranscriptionQuery(
        sources=_get_sources(*("ＡＢＣＤＥＦＧＨＩＪ" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = TranscriptionAnswer(text="ＫＬＭＮＯＰＱＲＳＴ｜")

    with raises(ValidationError, match="10 consecutive"):
        TranscriptionTestCase(query=query, answer=answer)


def test_answer_consensus_allows_contextual_span_rewrite():
    """A mapped contextual rewrite should not be treated as omitted text."""
    query = TranscriptionQuery(
        sources=_get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = TranscriptionAnswer(text="甲乙丙丁天地玄黃宇宙｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_consensus_rejects_three_consecutive_omissions():
    """Three consecutive omitted majority columns should trigger a retry."""
    scorer = TranscriptionAlignmentScorer()
    validation = scorer.score(tuple("甲乙丙丁戊己庚" for _ in range(3)), "甲乙丙丁")

    assert validation.longest_unpreserved_consensus_text == "戊己庚"
    assert not validation.preserves_consensus(2)


def test_answer_consensus_allows_scattered_contextual_corrections():
    """Scattered contextual rewrites should not trigger an omission retry."""
    source_text = "甲乙丙丁戊己庚辛壬癸"
    query = TranscriptionQuery(
        sources=_get_sources(*(source_text for _ in range(3))),
        speaker="Ａ" * len(source_text),
    )
    answer = TranscriptionAnswer(text="甲天丙丁地己庚玄壬癸｜")

    validation = TranscriptionAlignmentScorer().score(
        tuple(source.text for source in query.sources), answer.transcript
    )
    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert validation.majority_coverage == 0.7
    assert validation.longest_unpreserved_consensus_run == 0
    assert test_case.answer == answer


def test_answer_alignment_prioritizes_cross_source_support():
    """Single-source text should not pull an answer away from consensus columns."""
    validation = TranscriptionAlignmentScorer().score(
        ("　　　　", "　　甲乙", "甲乙甲乙"), "甲乙丙"
    )

    assert validation.mapped_majority_coverage == 1.0
    assert validation.majority_coverage == 1.0


def test_answer_consensus_accepts_compatibility_width_equivalence():
    """Halfwidth and fullwidth Latin characters should preserve the same evidence."""
    query = TranscriptionQuery(
        sources=_get_sources(*("June" for _ in range(3))), speaker="Ａ" * 4
    )
    answer = TranscriptionAnswer(text="Ｊｕｎｅ｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_consensus_ignores_nonlexical_source_columns():
    """Punctuation and spaces should not count as required answer evidence."""
    source_text = "甲，乙 丙，丁 戊，己"
    query = TranscriptionQuery(
        sources=_get_sources(source_text, source_text), speaker="Ａ" * len(source_text)
    )
    answer = TranscriptionAnswer(text="甲乙丙丁戊己｜")

    validation = TranscriptionAlignmentScorer().score(
        (source_text, source_text), answer.transcript
    )
    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert validation.majority_column_count == 6
    assert validation.majority_coverage == 1.0
    assert test_case.answer == answer


def test_answer_consensus_tolerates_one_contextual_spelling_replacement():
    """One mapped unsupported name correction should not fail a short request."""
    query = TranscriptionQuery(
        sources=_get_sources(*("膠兜依然係咁喺度" for _ in range(3))), speaker="Ａ" * 8
    )
    answer = TranscriptionAnswer(text="麥兜依然係咁喺度｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_consensus_does_not_reject_context_resolved_weak_columns():
    """Columns without a strict majority should remain diagnostic rather than fatal."""
    source_texts = ("菇時", "巫師", "　師", "古時", "　時", "姑絲")
    query = TranscriptionQuery(sources=_get_sources(*source_texts), speaker="ＡＡ")
    answer = TranscriptionAnswer(text="菇時｜")

    validation = TranscriptionAlignmentScorer().score(source_texts, answer.transcript)
    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert validation.majority_column_count == 0
    assert validation.majority_coverage == 1.0
    assert test_case.answer == answer


def test_empty_answer_rejects_only_long_consensus_spans():
    """An empty answer should retry only for a substantial consensus omission."""
    weak_query = TranscriptionQuery(
        sources=_get_sources("甲", "乙", "丙"), speaker="Ａ"
    )
    short_query = TranscriptionQuery(
        sources=_get_sources(*("甲乙" for _ in range(3))), speaker="ＡＡ"
    )
    long_query = TranscriptionQuery(
        sources=_get_sources(*("甲乙丙" for _ in range(3))), speaker="ＡＡＡ"
    )
    answer = TranscriptionAnswer(text="")

    assert TranscriptionTestCase(query=weak_query, answer=answer).answer == answer
    assert TranscriptionTestCase(query=short_query, answer=answer).answer == answer
    with raises(ValidationError, match="甲乙丙"):
        TranscriptionTestCase(query=long_query, answer=answer)


def test_empty_answer_allows_bare_majority_without_strong_consensus():
    """A bare four-of-six majority should not force noisy text into the answer."""
    query = TranscriptionQuery(
        sources=_get_sources(
            "甲乙丙", "甲乙丙", "甲乙丙", "甲乙丙", "丁戊己", "庚辛壬"
        ),
        speaker="ＡＡＡ",
    )
    answer = TranscriptionAnswer(text="")

    validation = TranscriptionAlignmentScorer().score(
        tuple(source.text for source in query.sources), answer.transcript
    )
    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert validation.majority_column_count == 3
    assert validation.longest_unpreserved_consensus_run == 0
    assert test_case.answer == answer
