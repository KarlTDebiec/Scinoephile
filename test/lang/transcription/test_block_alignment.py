#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block-level transcription alignment."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.block_aligner import BlockTranscriptionAligner
from scinoephile.llms.block_delineation import (
    BlockDelineationManager,
    BlockDelineationProcessor,
    BlockDelineationPrompt,
    BlockDelineationTestCase,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationManager,
    BlockPunctuationProcessor,
    BlockPunctuationPrompt,
    BlockPunctuationTestCase,
)


def _get_block() -> tuple[Series, AudioSeries]:
    """Get a three-subtitle guide and timing-aligned raw transcription.

    Returns:
        guide and raw transcription
    """
    guide = Series(
        events=[
            Subtitle(start=0, end=1_000, text="參考一"),
            Subtitle(start=1_000, end=2_000, text="參考二"),
            Subtitle(start=2_000, end=3_000, text="參考三"),
        ]
    )
    transcription = AudioSeries(
        audio=AudioSegment.silent(duration=3_000),
        events=[
            AudioSubtitle(start=0, end=1_000, text="甲乙"),
            AudioSubtitle(start=1_000, end=2_000, text="丙"),
            AudioSubtitle(start=2_000, end=3_000, text="丁"),
        ],
    )
    return guide, transcription


def _get_mock_processors() -> tuple[Mock, Mock]:
    """Get mock processors configured with concrete block test-case classes.

    Returns:
        delineation and punctuation processor mocks
    """
    delineation_processor = Mock(spec=BlockDelineationProcessor)
    delineation_processor.test_case_cls = BlockDelineationManager.get_test_case_cls(
        BlockDelineationPrompt()
    )
    delineation_processor.queryer = Mock()
    punctuation_processor = Mock(spec=BlockPunctuationProcessor)
    punctuation_processor.test_case_cls = BlockPunctuationManager.get_test_case_cls(
        BlockPunctuationPrompt()
    )
    punctuation_processor.queryer = Mock()
    return delineation_processor, punctuation_processor


def test_aligner_queries_each_operation_once_with_complete_indexed_block(
    tmp_path: Path,
):
    """Block alignment should issue two complete queries and apply sparse changes.

    Arguments:
        tmp_path: temporary cache root path
    """
    guide, transcription = _get_block()
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    provider.chat_completion.side_effect = [
        json.dumps(
            {"changes": [{"index": 1, "text": "甲"}, {"index": 2, "text": "乙丙"}]},
            ensure_ascii=False,
        ),
        json.dumps(
            {"changes": [{"index": 2, "text": "乙，丙"}, {"index": 3, "text": "丁！"}]},
            ensure_ascii=False,
        ),
    ]
    delineation_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    punctuation_processor = BlockPunctuationProcessor(
        BlockPunctuationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    alignment = aligner.align(guide, transcription)

    assert provider.chat_completion.call_count == 2
    delineation_messages = provider.chat_completion.call_args_list[0].args[0]
    assert json.loads(delineation_messages[1]["content"]) == {
        "guides": [
            {"index": 1, "text": "參考一"},
            {"index": 2, "text": "參考二"},
            {"index": 3, "text": "參考三"},
        ],
        "targets": [
            {"index": 1, "text": "甲乙"},
            {"index": 2, "text": "丙"},
            {"index": 3, "text": "丁"},
        ],
        "first_owned_index": 1,
        "last_owned_index": 2,
    }
    punctuation_messages = provider.chat_completion.call_args_list[1].args[0]
    assert json.loads(punctuation_messages[1]["content"])["targets"] == [
        {"index": 1, "text": "甲"},
        {"index": 2, "text": "乙丙"},
        {"index": 3, "text": "丁"},
    ]
    assert json.loads(punctuation_messages[1]["content"])["first_owned_index"] == 1
    assert json.loads(punctuation_messages[1]["content"])["last_owned_index"] == 3
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲",
        "乙，丙",
        "丁！",
    ]
    assert [(subtitle.start, subtitle.end) for subtitle in alignment.transcription] == [
        (0, 1_000),
        (1_000, 2_000),
        (2_000, 3_000),
    ]
    assert alignment.sync_groups == [([0], [0]), ([1], [1]), ([2], [2])]


def test_invalid_delineation_falls_back_and_punctuation_uses_timing_baseline():
    """Delineation fallback should retain timing assignments for punctuation."""
    guide, transcription = _get_block()
    delineation_processor, punctuation_processor = _get_mock_processors()

    def reject_delineation(test_case: BlockDelineationTestCase):
        """Return a semantically invalid delineation answer."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": 1, "text": "壞"}]},
            }
        )

    def punctuate_baseline(test_case: BlockPunctuationTestCase):
        """Punctuate the unchanged timing baseline."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": 1, "text": "甲乙！"}]},
            }
        )

    delineation_processor.queryer.side_effect = reject_delineation
    punctuation_processor.queryer.side_effect = punctuate_baseline
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, fallback_to_no_op=True
    )

    alignment = aligner.align(guide, transcription)

    fallback = delineation_processor.queryer.log_encountered_test_case.call_args.args[0]
    assert fallback.answer is not None
    assert fallback.answer.changes == []
    assert fallback.verified is False
    punctuation_query = punctuation_processor.queryer.call_args.args[0].query
    assert [target.text for target in punctuation_query.targets] == ["甲乙", "丙", "丁"]
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲乙！",
        "丙",
        "丁",
    ]


def test_invalid_punctuation_falls_back_to_delineated_text():
    """Punctuation fallback should retain the successful delineation output."""
    guide, transcription = _get_block()
    delineation_processor, punctuation_processor = _get_mock_processors()

    def delineate(test_case: BlockDelineationTestCase):
        """Return a valid boundary change."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {
                    "changes": [
                        {"index": 1, "text": "甲"},
                        {"index": 2, "text": "乙丙"},
                    ]
                },
            }
        )

    def reject_punctuation(test_case: BlockPunctuationTestCase):
        """Return a punctuation answer that changes target characters."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": 2, "text": "壞"}]},
            }
        )

    delineation_processor.queryer.side_effect = delineate
    punctuation_processor.queryer.side_effect = reject_punctuation
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, fallback_to_no_op=True
    )

    alignment = aligner.align(guide, transcription)

    fallback = punctuation_processor.queryer.log_encountered_test_case.call_args.args[0]
    assert fallback.answer is not None
    assert fallback.answer.changes == []
    assert fallback.verified is False
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲",
        "乙丙",
        "丁",
    ]


def test_provider_errors_do_not_trigger_no_op_fallback():
    """Operational LLM failures should propagate rather than become no-op data."""
    guide, transcription = _get_block()
    delineation_processor, punctuation_processor = _get_mock_processors()
    delineation_processor.queryer.side_effect = ScinoephileError("provider failed")
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, fallback_to_no_op=True
    )

    with raises(ScinoephileError, match="provider failed"):
        aligner.align(guide, transcription)

    delineation_processor.queryer.log_encountered_test_case.assert_not_called()
    punctuation_processor.queryer.assert_not_called()


def test_long_blocks_use_timing_gap_windows_and_reconcile_owned_outputs():
    """Long blocks should query overlapping windows and retain each owned output."""
    references = Series(
        events=[
            Subtitle(
                start=index * 1_000 + (3_000 if index >= 12 else 0),
                end=index * 1_000 + (3_000 if index >= 12 else 0) + 500,
                text=f"參考{index + 1}",
            )
            for index in range(25)
        ]
    )
    targets = [chr(0x4E00 + index) for index in range(25)]
    delineation_processor, punctuation_processor = _get_mock_processors()

    def delineate_window(test_case: BlockDelineationTestCase):
        """Move one character across the first window's final owned boundary."""
        answer: dict[str, list[dict[str, int | str]]] = {"changes": []}
        if test_case.query.first_owned_index == 1:
            answer = {
                "changes": [
                    {"index": 12, "text": targets[11] + targets[12]},
                    {"index": 13, "text": ""},
                ]
            }
        return type(test_case).model_validate(
            {**test_case.model_dump(mode="json"), "answer": answer}
        )

    def punctuate_window(test_case: BlockPunctuationTestCase):
        """Punctuate the first owned nonempty output in each window."""
        index = test_case.query.first_owned_index or 1
        if not test_case.query.targets[index - 1].text:
            index += 1
        text = test_case.query.targets[index - 1].text
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": index, "text": f"{text}！"}]},
            }
        )

    delineation_processor.queryer.side_effect = delineate_window
    punctuation_processor.queryer.side_effect = punctuate_window
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    delineated = aligner._delineate(list(references), targets)  # noqa: SLF001
    punctuated = aligner._punctuate(  # noqa: SLF001
        list(references), delineated
    )

    assert delineation_processor.queryer.call_count == 2
    first_query = delineation_processor.queryer.call_args_list[0].args[0].query
    second_query = delineation_processor.queryer.call_args_list[1].args[0].query
    assert len(first_query.guides) == 15
    assert (first_query.first_owned_index, first_query.last_owned_index) == (1, 12)
    assert len(second_query.guides) == 16
    assert (second_query.first_owned_index, second_query.last_owned_index) == (4, 15)
    assert delineated[11] == targets[11] + targets[12]
    assert delineated[12] == ""
    assert "".join(delineated) == "".join(targets)
    assert punctuated[0].endswith("！")
    assert punctuated[13].endswith("！")


def test_later_windows_inherit_prior_cuts_without_crossing():
    """Later windows should receive prior cuts as immutable left context."""
    references = Series(
        events=[
            Subtitle(
                start=index * 1_000, end=index * 1_000 + 500, text=f"參考{index + 1}"
            )
            for index in range(25)
        ]
    )
    targets = [chr(0x4E00 + index) for index in range(25)]
    delineation_processor, punctuation_processor = _get_mock_processors()

    def delineate_window(test_case: BlockDelineationTestCase):
        """Move the first cut beyond the next preliminary cut."""
        answer: dict[str, list[dict[str, int | str]]] = {"changes": []}
        if test_case.query.first_owned_index == 1:
            answer = {
                "changes": [
                    {"index": 12, "text": targets[11] + targets[12] + targets[13]},
                    {"index": 13, "text": ""},
                    {"index": 14, "text": ""},
                ]
            }
        return type(test_case).model_validate(
            {**test_case.model_dump(mode="json"), "answer": answer}
        )

    delineation_processor.queryer.side_effect = delineate_window
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    delineated = aligner._delineate(list(references), targets)  # noqa: SLF001

    second_query = delineation_processor.queryer.call_args_list[1].args[0].query
    assert second_query.targets[3].text == ""
    assert delineated[11] == targets[11] + targets[12] + targets[13]
    assert delineated[12:14] == ["", ""]
    assert "".join(delineated) == "".join(targets)


def test_window_boundaries_prefer_strong_nearby_timing_gaps():
    """Ownership cuts should flex toward timing gaps near nominal sizes."""
    gaps = {14: 4_000, 22: 3_000}
    current_start = 0
    references: list[Subtitle] = []
    for index in range(30):
        if index:
            current_start += gaps.get(index, 500)
        references.append(
            Subtitle(start=current_start, end=current_start + 500, text=str(index))
        )
        current_start += 500

    windows = BlockTranscriptionAligner._get_windows(references)  # noqa: SLF001

    assert [(window.owned_start, window.owned_end) for window in windows] == [
        (0, 14),
        (14, 22),
        (22, 30),
    ]
    assert [(window.start, window.end) for window in windows] == [
        (0, 17),
        (11, 25),
        (19, 30),
    ]
