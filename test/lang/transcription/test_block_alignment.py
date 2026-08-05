#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for block-level transcription alignment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from pydantic import ValidationError
from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.lang.transcription.block_aligner import (
    BlockTranscriptionAligner,
    _TimingBoundary,
)
from scinoephile.llms.block_delineation import (
    AdvisoryBlockDelineationProcessor,
    AdvisoryBlockDelineationPrompt,
    BlockDelineationManager,
    BlockDelineationProcessor,
    BlockDelineationPrompt,
    BlockDelineationTestCase,
    CandidateBlockDelineationProcessor,
    CandidateBlockDelineationPrompt,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationManager,
    BlockPunctuationProcessor,
    BlockPunctuationPrompt,
    BlockPunctuationTestCase,
    PositionalBlockPunctuationProcessor,
    PositionalBlockPunctuationPrompt,
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
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"changes": [{"index": 1, "shift": -1}]}, ensure_ascii=False),
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
        "boundaries": [
            {"index": 1, "original_offset": 2, "minimum_shift": -2, "maximum_shift": 2},
            {"index": 2, "original_offset": 3, "minimum_shift": -3, "maximum_shift": 1},
        ],
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


def test_aligner_can_skip_punctuation(tmp_path: Path):
    """Block alignment should retain delineated text without a punctuation query.

    Arguments:
        tmp_path: temporary cache root path
    """
    guide, transcription = _get_block()
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps(
        {"changes": [{"index": 1, "shift": -1}]}
    )
    delineation_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    aligner = BlockTranscriptionAligner(delineation_processor, None)

    alignment = aligner.align(guide, transcription)

    assert provider.chat_completion.call_count == 1
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲",
        "乙丙",
        "丁",
    ]


def test_candidate_alignment_selects_timed_cut_and_inserts_punctuation(tmp_path: Path):
    """Candidate mode should expose timed cuts and apply positional punctuation."""
    guide, transcription = _get_block()
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"changes": [{"index": 1, "shift": 1}]}),
        json.dumps(
            {
                "changes": [
                    {"index": 1, "edits": [{"position": 3, "punctuation": "！"}]}
                ]
            },
            ensure_ascii=False,
        ),
    ]
    delineation_processor = CandidateBlockDelineationProcessor(
        CandidateBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    punctuation_processor = PositionalBlockPunctuationProcessor(
        PositionalBlockPunctuationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, use_delineation_candidates=True
    )

    alignment = aligner.align(guide, transcription)

    delineation_query = json.loads(
        provider.chat_completion.call_args_list[0].args[0][1]["content"]
    )
    assert [
        candidate["shift"]
        for candidate in delineation_query["boundaries"][0]["candidates"]
    ] == [0, 1, 2]
    assert [subtitle.text for subtitle in alignment.transcription] == ["甲乙丙！", "丁"]


def test_advisory_alignment_ranks_timed_cuts_without_restricting_shift(tmp_path: Path):
    """Advisory mode should rank timed cuts but accept another legal boundary."""
    guide, transcription = _get_block()
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        json.dumps({"changes": [{"index": 1, "shift": -1}]}),
        json.dumps({"changes": []}),
    ]
    delineation_processor = AdvisoryBlockDelineationProcessor(
        AdvisoryBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    punctuation_processor = BlockPunctuationProcessor(
        BlockPunctuationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, use_delineation_suggestions=True
    )

    alignment = aligner.align(guide, transcription)

    delineation_query = json.loads(
        provider.chat_completion.call_args_list[0].args[0][1]["content"]
    )
    suggestions = delineation_query["boundaries"][0]["suggestions"]
    assert [suggestion["rank"] for suggestion in suggestions] == list(
        range(1, len(suggestions) + 1)
    )
    assert -1 not in [suggestion["shift"] for suggestion in suggestions]
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲",
        "乙丙",
        "丁",
    ]


def test_gated_advisory_highlights_only_stronger_timing_evidence():
    """Gated advisory mode should omit weak cuts and retain strong alternatives."""
    references = [
        Subtitle(start=0, end=1_000, text="參考一"),
        Subtitle(start=1_000, end=2_000, text="參考二"),
    ]
    targets = ["甲乙", "丙丁"]

    stronger_values = BlockTranscriptionAligner._get_advisory_boundary_values(  # noqa: SLF001
        references,
        targets,
        1,
        1,
        0,
        [
            _TimingBoundary(offset=1, time=1_100, pause=0),
            _TimingBoundary(offset=2, time=2_000, pause=0),
            _TimingBoundary(offset=3, time=1_200, pause=0),
        ],
        gated=True,
    )
    weak_values = BlockTranscriptionAligner._get_advisory_boundary_values(  # noqa: SLF001
        references,
        targets,
        1,
        1,
        0,
        [
            _TimingBoundary(offset=1, time=1_600, pause=0),
            _TimingBoundary(offset=2, time=1_100, pause=0),
            _TimingBoundary(offset=3, time=1_700, pause=0),
        ],
        gated=True,
    )
    missing_baseline_values = BlockTranscriptionAligner._get_advisory_boundary_values(  # noqa: SLF001
        references,
        targets,
        1,
        1,
        0,
        [
            _TimingBoundary(offset=1, time=4_000, pause=0),
            _TimingBoundary(offset=3, time=5_000, pause=0),
        ],
        gated=True,
    )

    stronger_suggestions = cast(
        "list[dict[str, object]]", stronger_values[0]["suggestions"]
    )
    assert [suggestion["shift"] for suggestion in stronger_suggestions] == [-1, 1, 0]
    assert weak_values[0]["suggestions"] == []
    assert missing_baseline_values[0]["suggestions"] == []


def test_candidate_boundaries_include_soft_speaker_change_evidence():
    """Actual diarized events should expose nonmandatory speaker evidence."""
    references = [
        Subtitle(start=0, end=2_000, text="參考一"),
        Subtitle(start=2_000, end=3_000, text="參考二"),
    ]
    transcription_events = []
    for index, (text, start, end, speaker, voice_activity_score) in enumerate(
        [
            ("甲", 0, 900, "SPEAKER_00", 0.05),
            ("乙", 900, 1_800, "SPEAKER_01", 0.6),
            ("丙", 2_100, 2_900, "SPEAKER_01", None),
        ]
    ):
        segment = TranscribedSegment(
            id=index,
            seek=0,
            start=start / 1000,
            end=end / 1000,
            text=text,
            words=[
                TranscribedWord(
                    text=text,
                    start=start / 1000,
                    end=end / 1000,
                    confidence=1.0,
                    following_voice_activity_score=voice_activity_score,
                    speaker=speaker,
                )
            ],
        )
        transcription_events.append(
            AudioSubtitle(start=start, end=end, text=text, segment=segment)
        )
    transcription = AudioSeries(
        audio=AudioSegment.silent(duration=3_000), events=transcription_events
    )
    alignment = TranscriptionAlignment(Series(events=references), transcription)
    timing_boundaries = BlockTranscriptionAligner._get_timing_boundaries(  # noqa: SLF001
        alignment, ["甲乙", "丙"]
    )

    assert [boundary.speaker_change for boundary in timing_boundaries] == [
        True,
        False,
        None,
    ]
    assert [boundary.voice_activity_score for boundary in timing_boundaries] == [
        0.05,
        0.6,
        None,
    ]

    values = BlockTranscriptionAligner._get_candidate_boundary_values(  # noqa: SLF001
        references, ["甲乙", "丙"], 1, 1, 0, timing_boundaries
    )

    candidates = cast("list[dict[str, object]]", values[0]["candidates"])
    speaker_candidate = next(
        candidate for candidate in candidates if candidate["offset"] == 1
    )
    baseline_candidate = next(
        candidate for candidate in candidates if candidate["shift"] == 0
    )
    assert speaker_candidate["speaker_change"] is True
    assert speaker_candidate["voice_activity_score"] == 0.05
    assert baseline_candidate["speaker_change"] is False
    assert baseline_candidate["voice_activity_score"] == 0.6


def test_suggestion_free_gated_advisory_uses_unrestricted_cache(tmp_path: Path):
    """Suggestion-free gated windows should share unrestricted cache identity.

    Arguments:
        tmp_path: temporary cache root path
    """
    guide, transcription = _get_block()
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps({"changes": []})
    advisory_processor = AdvisoryBlockDelineationProcessor(
        AdvisoryBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    unrestricted_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    gated_aligner = BlockTranscriptionAligner(
        advisory_processor,
        None,
        unrestricted_delineation_processor=unrestricted_processor,
        gate_delineation_suggestions=True,
        use_delineation_suggestions=True,
    )

    gated_aligner.align(guide, transcription)

    assert provider.chat_completion.call_count == 1
    assert provider.chat_completion.call_args.kwargs["operation"] == (
        "block-delineation"
    )
    query = json.loads(provider.chat_completion.call_args.args[0][1]["content"])
    assert all("suggestions" not in boundary for boundary in query["boundaries"])
    assert len(advisory_processor.queryer.encountered_test_cases) == 1
    assert len(unrestricted_processor.queryer.encountered_test_cases) == 1

    fresh_unrestricted_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    unrestricted_aligner = BlockTranscriptionAligner(fresh_unrestricted_processor, None)

    unrestricted_aligner.align(guide, transcription)

    assert provider.chat_completion.call_count == 1
    assert len(fresh_unrestricted_processor.queryer.encountered_test_cases) == 1


def test_suggestion_free_gated_advisory_migrates_advisory_cache(tmp_path: Path):
    """Existing suggestion-free advisory responses should seed unrestricted cache.

    Arguments:
        tmp_path: temporary cache root path
    """
    guide, transcription = _get_block()
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps({"changes": []})
    legacy_advisory_processor = AdvisoryBlockDelineationProcessor(
        AdvisoryBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    legacy_aligner = BlockTranscriptionAligner(
        legacy_advisory_processor,
        None,
        gate_delineation_suggestions=True,
        use_delineation_suggestions=True,
    )
    legacy_aligner.align(guide, transcription)
    assert provider.chat_completion.call_count == 1

    advisory_processor = AdvisoryBlockDelineationProcessor(
        AdvisoryBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    unrestricted_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    gated_aligner = BlockTranscriptionAligner(
        advisory_processor,
        None,
        unrestricted_delineation_processor=unrestricted_processor,
        gate_delineation_suggestions=True,
        use_delineation_suggestions=True,
    )
    gated_aligner.align(guide, transcription)

    fresh_unrestricted_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    BlockTranscriptionAligner(fresh_unrestricted_processor, None).align(
        guide, transcription
    )

    assert provider.chat_completion.call_count == 1


def test_gated_advisory_with_suggestions_uses_advisory_query(tmp_path: Path):
    """Gated windows with strong timing evidence should retain advisory queries.

    Arguments:
        tmp_path: temporary cache root path
    """
    references = [
        Subtitle(start=0, end=1_000, text="參考一"),
        Subtitle(start=1_000, end=2_000, text="參考二"),
    ]
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = json.dumps({"changes": []})
    advisory_processor = AdvisoryBlockDelineationProcessor(
        AdvisoryBlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    unrestricted_processor = BlockDelineationProcessor(
        BlockDelineationPrompt(), provider=provider, cache_root_path=tmp_path
    )
    aligner = BlockTranscriptionAligner(
        advisory_processor,
        None,
        unrestricted_delineation_processor=unrestricted_processor,
        gate_delineation_suggestions=True,
        use_delineation_suggestions=True,
    )

    output = aligner._delineate_window(  # noqa: SLF001
        references,
        ["甲乙", "丙丁"],
        first_owned_index=1,
        last_owned_index=1,
        window_index=1,
        window_offset=0,
        timing_boundaries=[
            _TimingBoundary(offset=1, time=1_100, pause=0),
            _TimingBoundary(offset=2, time=2_000, pause=0),
            _TimingBoundary(offset=3, time=1_200, pause=0),
        ],
    )

    assert output == ["甲乙", "丙丁"]
    assert provider.chat_completion.call_count == 1
    assert provider.chat_completion.call_args.kwargs["operation"] == (
        "advisory-block-delineation"
    )
    query = json.loads(provider.chat_completion.call_args.args[0][1]["content"])
    assert query["boundaries"][0]["suggestions"]
    assert not unrestricted_processor.queryer.encountered_test_cases


def test_invalid_delineation_falls_back_and_punctuation_uses_timing_baseline():
    """Delineation fallback should retain timing assignments for punctuation."""
    guide, transcription = _get_block()
    delineation_processor, punctuation_processor = _get_mock_processors()

    def reject_delineation(test_case: BlockDelineationTestCase):
        """Return a semantically invalid delineation answer."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": 1, "shift": 99}]},
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
    assert delineation_processor.queryer.log_encountered_test_case.call_args.kwargs == {
        "skip_output_quality_validation": True
    }
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
                "answer": {"changes": [{"index": 1, "shift": -1}]},
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
    assert punctuation_processor.queryer.log_encountered_test_case.call_args.kwargs == {
        "skip_output_quality_validation": True
    }
    assert [subtitle.text for subtitle in alignment.transcription] == [
        "甲",
        "乙丙",
        "丁",
    ]


def test_punctuation_masks_excessive_repeat_runs_and_preserves_original_text():
    """Punctuation should not ask an LLM to reproduce pathological repeats."""
    delineation_processor, punctuation_processor = _get_mock_processors()
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)
    targets = ["甲", "嚟" * 54, "乙"]

    def punctuate_unmasked_targets(test_case: BlockPunctuationTestCase):
        """Punctuate normal targets while leaving the masked target empty."""
        assert [target.text for target in test_case.query.targets] == ["甲", "", "乙"]
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {
                    "changes": [
                        {"index": 1, "text": "甲！"},
                        {"index": 3, "text": "乙？"},
                    ]
                },
            }
        )

    punctuation_processor.queryer.side_effect = punctuate_unmasked_targets
    window = BlockTranscriptionAligner._get_windows(  # noqa: SLF001
        [
            Subtitle(start=index * 1_000, end=(index + 1) * 1_000, text=str(index))
            for index in range(3)
        ]
    )[0]

    output = aligner._punctuate_window(  # noqa: SLF001
        ["參考一", "參考二", "參考三"], targets, window, 1
    )

    assert output == ["甲！", "嚟" * 54, "乙？"]


def test_punctuation_clears_empty_and_punctuation_only_targets_deterministically():
    """Punctuation should clear empty fragments without asking the LLM to copy them."""
    delineation_processor, punctuation_processor = _get_mock_processors()
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    def punctuate_nonempty_target(test_case: BlockPunctuationTestCase):
        """Punctuate the only nonempty target in the query."""
        assert [target.text for target in test_case.query.targets] == ["", "", "甲"]
        return type(test_case).model_validate(
            {
                **test_case.model_dump(mode="json"),
                "answer": {"changes": [{"index": 3, "text": "甲！"}]},
            }
        )

    punctuation_processor.queryer.side_effect = punctuate_nonempty_target
    window = BlockTranscriptionAligner._get_windows(  # noqa: SLF001
        [
            Subtitle(start=index * 1_000, end=(index + 1) * 1_000, text=str(index))
            for index in range(3)
        ]
    )[0]

    output = aligner._punctuate_window(  # noqa: SLF001
        ["參考一", "參考二", "參考三"], ["", "， ", "甲"], window, 1
    )

    assert output == ["", "", "甲！"]


def test_aligner_clears_punctuation_only_targets_before_delineation():
    """Punctuation-only timing targets should never reach either LLM query."""
    guide, transcription = _get_block()
    transcription[0].text = "， "
    delineation_processor, punctuation_processor = _get_mock_processors()

    def delineate(test_case: BlockDelineationTestCase):
        """Confirm deterministic cleanup occurs before delineation."""
        assert [target.text for target in test_case.query.targets] == ["", "丙", "丁"]
        return type(test_case).model_validate(
            {**test_case.model_dump(mode="json"), "answer": {"changes": []}}
        )

    def punctuate(test_case: BlockPunctuationTestCase):
        """Confirm the cleaned empty target remains empty for punctuation."""
        assert [target.text for target in test_case.query.targets] == ["", "丙", "丁"]
        return type(test_case).model_validate(
            {**test_case.model_dump(mode="json"), "answer": {"changes": []}}
        )

    delineation_processor.queryer.side_effect = delineate
    punctuation_processor.queryer.side_effect = punctuate
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    alignment = aligner.align(guide, transcription)

    assert [subtitle.text for subtitle in alignment.transcription] == ["丙", "丁"]


def test_punctuation_skips_query_when_all_owned_targets_are_deterministic():
    """Punctuation should not query when every owned target becomes empty."""
    delineation_processor, punctuation_processor = _get_mock_processors()
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)
    window = BlockTranscriptionAligner._get_windows(  # noqa: SLF001
        [
            Subtitle(start=index * 1_000, end=(index + 1) * 1_000, text=str(index))
            for index in range(2)
        ]
    )[0]

    output = aligner._punctuate_window(  # noqa: SLF001
        ["參考一", "參考二"], ["。", "  "], window, 1
    )

    assert output == ["", ""]
    punctuation_processor.queryer.assert_not_called()


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


def test_structured_provider_errors_trigger_no_op_fallback():
    """Provider-wrapped structured validation failures should use fallback."""
    guide, transcription = _get_block()
    delineation_processor, punctuation_processor = _get_mock_processors()

    def reject_structured_response(_: BlockDelineationTestCase):
        """Raise the provider error used for an invalid structured response."""
        try:
            BlockDelineationTestCase.answer_cls.model_validate(
                {"changes": [{"index": 0, "shift": 1}]}
            )
        except ValidationError as exc:
            raise ScinoephileError("invalid structured content") from exc
        raise AssertionError("Invalid structured answer unexpectedly validated.")

    delineation_processor.queryer.side_effect = reject_structured_response
    punctuation_processor.queryer.return_value = (
        BlockPunctuationTestCase.model_validate(
            {
                "query": {
                    "guides": [
                        {"index": index, "text": subtitle.text}
                        for index, subtitle in enumerate(guide, 1)
                    ],
                    "targets": [
                        {"index": index, "text": subtitle.text}
                        for index, subtitle in enumerate(transcription, 1)
                    ],
                },
                "answer": {"changes": []},
            }
        )
    )
    aligner = BlockTranscriptionAligner(
        delineation_processor, punctuation_processor, fallback_to_no_op=True
    )

    aligner.align(guide, transcription)

    fallback = delineation_processor.queryer.log_encountered_test_case.call_args.args[0]
    assert fallback.answer is not None
    assert fallback.answer.changes == []
    punctuation_processor.queryer.assert_called_once()


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
        answer: dict[str, list[dict[str, int]]] = {"changes": []}
        if test_case.query.first_owned_index == 1:
            answer = {"changes": [{"index": 12, "shift": 1}]}
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

    assert delineation_processor.queryer.call_count == 3
    first_query = delineation_processor.queryer.call_args_list[0].args[0].query
    second_query = delineation_processor.queryer.call_args_list[1].args[0].query
    third_query = delineation_processor.queryer.call_args_list[2].args[0].query
    assert len(first_query.guides) == 15
    assert (first_query.first_owned_index, first_query.last_owned_index) == (1, 12)
    assert len(second_query.guides) == 12
    assert (second_query.first_owned_index, second_query.last_owned_index) == (4, 9)
    assert len(third_query.guides) == 10
    assert (third_query.first_owned_index, third_query.last_owned_index) == (4, 9)
    assert delineated[11] == targets[11] + targets[12]
    assert delineated[12] == ""
    assert "".join(delineated) == "".join(targets)
    assert punctuated[0].endswith("！")
    assert punctuated[13].endswith("！")
    assert punctuated[18].endswith("！")


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
        answer: dict[str, list[dict[str, int]]] = {"changes": []}
        if test_case.query.first_owned_index == 1:
            answer = {"changes": [{"index": 9, "shift": 2}]}
        return type(test_case).model_validate(
            {**test_case.model_dump(mode="json"), "answer": answer}
        )

    delineation_processor.queryer.side_effect = delineate_window
    aligner = BlockTranscriptionAligner(delineation_processor, punctuation_processor)

    delineated = aligner._delineate(list(references), targets)  # noqa: SLF001

    second_query = delineation_processor.queryer.call_args_list[1].args[0].query
    assert second_query.targets[3].text == ""
    assert delineated[8] == targets[8] + targets[9] + targets[10]
    assert delineated[9:11] == ["", ""]
    assert "".join(delineated) == "".join(targets)


def test_window_boundaries_prefer_strong_nearby_timing_gaps():
    """Ownership cuts should flex toward timing gaps near nominal sizes."""
    gaps = {12: 4_000, 20: 3_000}
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
        (0, 12),
        (12, 20),
        (20, 30),
    ]
    assert [(window.start, window.end) for window in windows] == [
        (0, 15),
        (9, 23),
        (17, 30),
    ]
    assert all(window.end - window.start <= 15 for window in windows)


def test_window_planning_caps_query_and_owned_sizes():
    """All long block sizes should produce complete bounded ownership."""
    for subtitle_count in range(13, 101):
        references = [
            Subtitle(start=index * 1_000, end=index * 1_000 + 500, text=str(index))
            for index in range(subtitle_count)
        ]

        windows = BlockTranscriptionAligner._get_windows(references)  # noqa: SLF001
        owned_ranges = [
            range(window.owned_start, window.owned_end) for window in windows
        ]
        owned_indexes = [index for owned_range in owned_ranges for index in owned_range]

        assert owned_indexes == list(range(subtitle_count))
        assert all(window.end - window.start <= 15 for window in windows)
        assert windows[0].owned_end - windows[0].owned_start <= 12
        assert windows[-1].owned_end - windows[-1].owned_start <= 12
        assert all(
            window.owned_end - window.owned_start <= 9 for window in windows[1:-1]
        )
