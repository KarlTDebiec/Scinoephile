#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transcription LLM models and processing."""

from __future__ import annotations

import json
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.llms.transcription import (
    TranscriptionAnswer,
    TranscriptionManager,
    TranscriptionProcessor,
    TranscriptionPrompt,
    TranscriptionQuery,
    TranscriptionSource,
    TranscriptionTestCase,
)
from scinoephile.llms.transcription.validation import get_transcription_validation

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


def test_transcription_rejects_answer_punctuation():
    """Transcription rejects punctuation while its answer model remains tolerant."""
    test_case_cls = TranscriptionManager.get_test_case_cls(_LOCALIZED_PROMPT)

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


def test_query_accepts_equal_width_language_singing_and_music_rows():
    """Optional FireRed traces should retain the alignment's exact width."""
    query_cls = TranscriptionManager.get_query_cls(TranscriptionManager.base_prompt)

    query = cast(
        TranscriptionQuery,
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


def test_query_key_includes_optional_traces_omitted_from_serialization():
    """Query keys should distinguish absent and populated optional traces."""
    query = TranscriptionQuery(sources=_get_sources("甲", "甲"), speaker="Ａ")
    traced_query = TranscriptionQuery(
        sources=_get_sources("甲", "甲"), speaker="Ａ", language_trace="粵"
    )

    assert "language_trace" not in query.model_dump(mode="json")
    assert query.key != traced_query.key


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


def test_processor_no_op_returns_empty_answer():
    """No-op mode should omit aligned content without selecting a source."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider, no_op=True)

    answer = processor.process(_get_sources("甲　・乙", "甲丙・乙"), "ＡＡ・Ａ")

    assert answer.text == ""
    provider.chat_completion.assert_not_called()


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
    processor = TranscriptionProcessor(_LOCALIZED_PROMPT, provider=provider)

    answer = processor.process(
        _get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))), "Ａ" * 10
    )

    assert answer.transcript == "甲乙丙丁戊己庚辛壬癸"
    retry_messages = provider.chat_completion.call_args.args[0]
    assert "preserves only 40.0%" in retry_messages[-1]["content"]


def test_answer_coverage_allows_locally_supported_character_corrections():
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


def test_answer_coverage_rejects_equal_length_majority_replacement():
    """Unrelated equal-length text should not count as preserved evidence."""
    query = TranscriptionQuery(
        sources=_get_sources(*("ＡＢＣＤＥＦＧＨＩＪ" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = TranscriptionAnswer(text="ＫＬＭＮＯＰＱＲＳＴ｜")

    with raises(ValidationError, match="preserves only 0.0%"):
        TranscriptionTestCase(query=query, answer=answer)


def test_answer_coverage_rejects_insertions_replacing_missing_majority_span():
    """Inserted text should not compensate for omitted majority characters."""
    query = TranscriptionQuery(
        sources=_get_sources(*("甲乙丙丁戊己庚辛壬癸" for _ in range(3))),
        speaker="Ａ" * 10,
    )
    answer = TranscriptionAnswer(text="甲乙丙丁天地玄黃宇宙｜")

    with raises(ValidationError, match="preserves only 40.0%"):
        TranscriptionTestCase(query=query, answer=answer)


def test_answer_coverage_accepts_compatibility_width_equivalence():
    """Halfwidth and fullwidth Latin characters should preserve the same evidence."""
    query = TranscriptionQuery(
        sources=_get_sources(*("June" for _ in range(3))), speaker="Ａ" * 4
    )
    answer = TranscriptionAnswer(text="Ｊｕｎｅ｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_coverage_tolerates_one_contextual_spelling_replacement():
    """One mapped unsupported name correction should not fail a short request."""
    query = TranscriptionQuery(
        sources=_get_sources(*("膠兜依然係咁喺度" for _ in range(3))), speaker="Ａ" * 8
    )
    answer = TranscriptionAnswer(text="麥兜依然係咁喺度｜")

    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert test_case.answer == answer


def test_answer_coverage_does_not_reject_context_resolved_weak_columns():
    """Columns without a strict majority should remain diagnostic rather than fatal."""
    source_texts = ("菇時", "巫師", "　師", "古時", "　時", "姑絲")
    query = TranscriptionQuery(sources=_get_sources(*source_texts), speaker="ＡＡ")
    answer = TranscriptionAnswer(text="菇時｜")

    validation = get_transcription_validation(
        source_texts, answer.transcript, Language.yue_hant
    )
    test_case = TranscriptionTestCase(query=query, answer=answer)

    assert validation.majority_column_count == 0
    assert validation.majority_coverage == 1.0
    assert test_case.answer == answer


def test_empty_answer_requires_absent_majority_evidence():
    """An empty answer should fail only when strict-majority speech is present."""
    weak_query = TranscriptionQuery(
        sources=_get_sources("甲", "乙", "丙"), speaker="Ａ"
    )
    strong_query = TranscriptionQuery(
        sources=_get_sources("甲", "甲", "甲"), speaker="Ａ"
    )
    answer = TranscriptionAnswer(text="")

    assert TranscriptionTestCase(query=weak_query, answer=answer).answer == answer
    with raises(ValidationError, match="preserves only 0.0%"):
        TranscriptionTestCase(query=strong_query, answer=answer)
