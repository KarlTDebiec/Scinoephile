#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-free timed multi-source transcription."""

from __future__ import annotations

from unittest.mock import Mock

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    TranscribedWord,
    Transcriber,
    TranscriptionEmptyError,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.multisource import UnguidedMultiSourceTranscriber
from scinoephile.llms.multi_review import MultiReviewProcessor


def _get_segment(
    text: str, start: float, end: float, *, with_words: bool = True
) -> TranscribedSegment:
    """Get one timestamped transcription segment."""
    words = None
    if with_words:
        words = [TranscribedWord(text=text, start=start, end=end, confidence=1.0)]
    return TranscribedSegment(
        id=0, seek=0, start=start, end=end, text=text, words=words
    )


def _get_transcriber(
    *,
    reviewer: MultiReviewProcessor | None = None,
    aligner: CtcAligner | None = None,
    sources: dict[str, Transcriber] | None = None,
) -> UnguidedMultiSourceTranscriber:
    """Get a multi-source transcriber with mocked dependencies."""
    if reviewer is None:
        reviewer = Mock(spec=MultiReviewProcessor)
    if aligner is None:
        aligner = Mock(spec=CtcAligner)
    if sources is None:
        sources = {"whisper": Mock(spec=Transcriber), "mimo": Mock(spec=Transcriber)}
    return UnguidedMultiSourceTranscriber(
        language=Language.yue_hant,
        transcribers=sources,
        reviewer=reviewer,
        aligner=aligner,
    )


def test_merge_uses_timing_only_windows_then_realigns_consensus():
    """Test source evidence is time-correlated before one fresh CTC alignment."""
    audio = AudioSegment.silent(duration=25_000)
    reviewer = Mock(spec=MultiReviewProcessor)
    reviewer.process.return_value = Series(
        events=[
            Subtitle(start=0, end=10_000, text="甲"),
            Subtitle(start=10_000, end=20_000, text="乙"),
            Subtitle(start=20_000, end=25_000, text="丙"),
        ]
    )
    aligner = Mock(
        spec=CtcAligner,
        side_effect=[
            [_get_segment("甲", 0.5, 2.0)],
            [_get_segment("乙", 1.0, 2.0)],
            [_get_segment("丙", 1.0, 3.0)],
        ],
    )
    transcriber = _get_transcriber(reviewer=reviewer, aligner=aligner)

    output = transcriber.merge(
        {
            "whisper": [_get_segment("甲", 1.0, 2.0), _get_segment("乙", 11.0, 12.0)],
            "mimo": [
                _get_segment("錯", 0.0, 20.0),
                _get_segment("乙二", 12.0, 13.0),
                _get_segment("丙", 21.0, 22.0, with_words=False),
            ],
        },
        audio,
    )

    assert [
        (segment.id, segment.start, segment.end, segment.text) for segment in output
    ] == [(0, 0.5, 2.0, "甲"), (1, 11.0, 12.0, "乙"), (2, 21.0, 23.0, "丙")]
    source_series, guide = reviewer.process.call_args.args
    assert [(event.start, event.end, event.text) for event in guide] == [
        (0, 10_000, "00:00.000–00:10.000"),
        (10_000, 20_000, "00:10.000–00:20.000"),
        (20_000, 25_000, "00:20.000–00:25.000"),
    ]
    assert [event.text for event in source_series["whisper"]] == ["甲", "乙"]
    assert [event.text for event in source_series["mimo"]] == ["錯乙二", "丙"]
    assert [len(call.args[0]) for call in aligner.call_args_list] == [
        10_000,
        10_000,
        5_000,
    ]
    assert [call.args[1] for call in aligner.call_args_list] == ["甲", "乙", "丙"]


def test_call_runs_sources_and_merges_successful_outputs():
    """Test every source sees identical audio and successful evidence is merged."""
    audio = AudioSegment.silent(duration=1_000)
    whisper_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    whisper = Mock(spec=Transcriber, return_value=whisper_segments)
    mimo = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    qwen = Mock(spec=Transcriber, return_value=qwen_segments)
    transcriber = _get_transcriber(
        sources={"whisper": whisper, "mimo": mimo, "qwen": qwen}
    )
    expected = [_get_segment("甲乙", 0.1, 0.5)]
    transcriber.merge = Mock(return_value=expected)

    output = transcriber(audio)

    assert output is expected
    whisper.assert_called_once_with(audio)
    mimo.assert_called_once_with(audio)
    qwen.assert_called_once_with(audio)
    transcriber.merge.assert_called_once_with(
        {"whisper": whisper_segments, "qwen": qwen_segments}, audio
    )


def test_call_falls_back_to_only_successful_source():
    """Test a single successful source remains usable without an LLM query."""
    audio = AudioSegment.silent(duration=1_000)
    segments = [_get_segment("甲", 0.1, 0.4)]
    whisper = Mock(spec=Transcriber, return_value=segments)
    mimo = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    reviewer = Mock(spec=MultiReviewProcessor)
    aligner = Mock(spec=CtcAligner)
    transcriber = _get_transcriber(
        reviewer=reviewer, aligner=aligner, sources={"whisper": whisper, "mimo": mimo}
    )

    output = transcriber(audio)

    assert output is segments
    reviewer.process.assert_not_called()
    aligner.assert_not_called()


def test_call_rejects_all_empty_sources():
    """Test no source output becomes a conventional empty-transcription error."""
    empty = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    transcriber = _get_transcriber(sources={"whisper": empty, "mimo": empty})

    with raises(TranscriptionEmptyError, match="All unguided transcription sources"):
        transcriber(AudioSegment.silent(duration=1_000))


def test_merge_rejects_blank_review_output():
    """Test a blank consensus is rejected before CTC alignment."""
    reviewer = Mock(spec=MultiReviewProcessor)
    reviewer.process.return_value = Series(
        events=[Subtitle(start=0, end=1_000, text="")]
    )
    aligner = Mock(spec=CtcAligner)
    transcriber = _get_transcriber(reviewer=reviewer, aligner=aligner)

    with raises(TranscriptionEmptyError, match="review produced no usable text"):
        transcriber.merge(
            {
                "whisper": [_get_segment("甲", 0.1, 0.4)],
                "mimo": [_get_segment("乙", 0.2, 0.5)],
            },
            AudioSegment.silent(duration=1_000),
        )

    aligner.assert_not_called()


def test_init_rejects_fewer_than_two_sources():
    """Test multi-source construction enforces its minimum source count."""
    with raises(ValueError, match="at least two sources"):
        _get_transcriber(sources={"whisper": Mock(spec=Transcriber)})


def test_merge_rejects_fewer_than_two_sources():
    """Test direct merging also enforces its minimum source count."""
    transcriber = _get_transcriber()

    with raises(ScinoephileError, match="at least two sources"):
        transcriber.merge(
            {"whisper": [_get_segment("甲", 0.1, 0.4)]},
            AudioSegment.silent(duration=1_000),
        )
