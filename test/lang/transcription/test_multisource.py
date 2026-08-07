#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-free aligned multi-source transcription."""

from __future__ import annotations

from unittest.mock import Mock

from pydub import AudioSegment
from pytest import approx, raises

from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentToken,
    TimedMultiSequenceAlignment,
)
from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    TranscribedWord,
    Transcriber,
    TranscriptionAlignmentIncompleteError,
    TranscriptionEmptyError,
    TranscriptionInferenceError,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.transcription.multisource import MultiSourceTranscriber
from scinoephile.llms.aligned_transcription_merge import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeProcessor,
)


def _get_segment(
    text: str,
    start: float,
    end: float,
    *,
    compression_ratio: float | None = None,
    with_words: bool = True,
) -> TranscribedSegment:
    """Get one timestamped transcription segment."""
    words = None
    if with_words:
        words = [TranscribedWord(text=text, start=start, end=end, confidence=1.0)]
    return TranscribedSegment(
        id=0,
        seek=0,
        start=start,
        end=end,
        text=text,
        compression_ratio=compression_ratio,
        words=words,
    )


def _get_answer(*texts: str) -> AlignedTranscriptionMergeAnswer:
    """Get one merged answer from punctuated subtitle text."""
    return AlignedTranscriptionMergeAnswer(text="".join(text + "｜" for text in texts))


def _get_transcriber(
    *,
    merger: AlignedTranscriptionMergeProcessor | None = None,
    ctc_aligner: CtcAligner | None = None,
    sources: dict[str, Transcriber] | None = None,
) -> MultiSourceTranscriber:
    """Get a multi-source transcriber with mocked dependencies."""
    if merger is None:
        merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    if ctc_aligner is None:
        ctc_aligner = Mock(spec=CtcAligner)
    if sources is None:
        sources = {"whisper": Mock(spec=Transcriber), "mimo": Mock(spec=Transcriber)}
    return MultiSourceTranscriber(
        language=Language.yue_hant,
        transcribers=sources,
        merger=merger,
        ctc_aligner=ctc_aligner,
    )


def test_merge_aligns_flat_rows_then_ctc_times_llm_subtitle_splits():
    """The LLM's splits should be retained after one request-level CTC pass."""
    audio = AudioSegment.silent(duration=3_000)
    request_answer = _get_answer("甲。", "乙！")
    merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    merger.process.return_value = request_answer
    merger.last_request_spans = ((0, 2),)
    merger.last_request_answers = (request_answer,)
    ctc_aligner = Mock(
        spec=CtcAligner, return_value=[_get_segment("甲。乙！", 0.5, 2.5)]
    )
    transcriber = _get_transcriber(merger=merger, ctc_aligner=ctc_aligner)

    output = transcriber.merge(
        {
            "whisper": [_get_segment("甲乙", 0.2, 2.2)],
            "mimo": [_get_segment("甲乙", 0.3, 2.3)],
        },
        audio,
    )

    assert [(segment.id, segment.text) for segment in output] == [
        (0, "甲。"),
        (1, "乙！"),
    ]
    assert [(segment.start, segment.end) for segment in output] == [
        (0.5, 1.5),
        (1.5, 2.5),
    ]
    ctc_aligner.assert_called_once_with(audio, "甲。乙！")
    merge_sources, speaker = merger.process.call_args.args
    assert [source.name for source in merge_sources] == ["whisper", "mimo"]
    assert [source.text for source in merge_sources] == ["甲乙", "甲乙"]
    assert len(speaker) == 2


def test_merge_uses_long_pause_boundaries_as_separate_ctc_windows():
    """Each LLM request should be aligned only within its VAD-bounded audio span."""
    audio = AudioSegment.silent(duration=3_000)
    first_answer = _get_answer("甲。")
    second_answer = _get_answer("乙。")
    merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    merger.process.return_value = _get_answer("甲。", "乙。")
    merger.last_request_spans = ((0, 1), (5, 6))
    merger.last_request_answers = (first_answer, second_answer)
    ctc_aligner = Mock(
        spec=CtcAligner,
        side_effect=[
            [_get_segment("甲。", 0.1, 0.4)],
            [_get_segment("乙。", 0.2, 0.7)],
        ],
    )
    transcriber = _get_transcriber(merger=merger, ctc_aligner=ctc_aligner)

    output = transcriber.merge(
        {
            "whisper": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.4)],
            "mimo": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.4)],
        },
        audio,
        pause_intervals_seconds=((0.5, 1.5),),
    )

    assert [(segment.start, segment.end, segment.text) for segment in output] == [
        (0.1, 0.4, "甲。"),
        (1.7, 2.2, "乙。"),
    ]
    assert [len(call.args[0]) for call in ctc_aligner.call_args_list] == [500, 1_500]
    assert [call.args[1] for call in ctc_aligner.call_args_list] == ["甲。", "乙。"]


def test_timing_skips_only_request_whose_evidence_is_beyond_audio():
    """A trailing ASR hallucination should not discard an otherwise valid block."""
    audio = AudioSegment.silent(duration=1_000)
    first_answer = _get_answer("甲。")
    trailing_answer = _get_answer("幻。")
    merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    merger.last_request_spans = ((0, 1), (2, 3))
    merger.last_request_answers = (first_answer, trailing_answer)
    ctc_aligner = Mock(spec=CtcAligner, return_value=[_get_segment("甲。", 0.1, 0.4)])
    transcriber = _get_transcriber(merger=merger, ctc_aligner=ctc_aligner)
    alignment = TimedMultiSequenceAlignment(
        source_names=("whisper", "mimo"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.1, 0.4),
                    TimedAlignmentToken("甲", 0.1, 0.4),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(1.2, 1.5)),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("幻", 1.6, 1.8),
                    TimedAlignmentToken("幻", 1.6, 1.8),
                )
            ),
        ),
    )

    output = transcriber._get_timed_answer_segments(  # noqa: SLF001
        audio, alignment, _get_answer("甲。", "幻。")
    )

    assert [(segment.text, segment.start, segment.end) for segment in output] == [
        ("甲。", 0.1, 0.4)
    ]
    ctc_aligner.assert_called_once_with(audio, "甲。")


def test_request_interval_falls_back_to_in_audio_lexical_timing():
    """Nonchronological pause columns should not hide usable lexical evidence."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("whisper", "mimo"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.1, 0.4),
                    TimedAlignmentToken("甲", 0.1, 0.4),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(1.2, 1.5)),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("乙", 0.6, 0.8),
                    TimedAlignmentToken("乙", 0.6, 0.8),
                )
            ),
        ),
    )

    interval = MultiSourceTranscriber._get_request_interval(  # noqa: SLF001
        alignment, (2, 3), 1.0
    )

    assert interval == (0.35, 1.0)


def test_timing_retries_incomplete_request_against_unconsumed_block():
    """A short request window should be retried after prior merged output."""
    audio = AudioSegment.silent(duration=3_000)
    first_answer = _get_answer("甲。")
    second_answer = _get_answer("乙。")
    third_answer = _get_answer("丙。")
    answer = _get_answer("甲。", "乙。", "丙。")
    merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    merger.last_request_spans = ((0, 1), (2, 3), (4, 5))
    merger.last_request_answers = (first_answer, second_answer, third_answer)
    ctc_aligner = Mock(
        spec=CtcAligner,
        side_effect=[
            [_get_segment("甲。", 0.1, 0.4)],
            TranscriptionAlignmentIncompleteError(
                "CTC alignment did not reach all tokens."
            ),
            [_get_segment("乙。", 1.4, 2.0)],
            [_get_segment("丙。", 0.1, 0.3)],
        ],
    )
    transcriber = _get_transcriber(merger=merger, ctc_aligner=ctc_aligner)
    alignment = TimedMultiSequenceAlignment(
        source_names=("whisper", "mimo"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.1, 0.4),
                    TimedAlignmentToken("甲", 0.1, 0.4),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(0.5, 1.5)),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("乙", 1.8, 2.4),
                    TimedAlignmentToken("乙", 1.8, 2.4),
                )
            ),
            TimedAlignmentColumn((None, None), pause_interval_seconds=(2.0, 2.1)),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("丙", 2.5, 2.8),
                    TimedAlignmentToken("丙", 2.5, 2.8),
                )
            ),
        ),
    )

    output = transcriber._get_timed_answer_segments(  # noqa: SLF001
        audio, alignment, answer
    )

    assert [segment.text for segment in output] == ["甲。", "乙。", "丙。"]
    assert [segment.start for segment in output] == approx([0.1, 1.8, 2.5])
    assert [segment.end for segment in output] == approx([0.4, 2.4, 2.7])
    assert [len(call.args[0]) for call in ctc_aligner.call_args_list] == [
        500,
        500,
        2_600,
        600,
    ]


def test_call_runs_sources_and_merges_successful_outputs():
    """Every source should see identical audio and successful evidence be merged."""
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
        {"whisper": whisper_segments, "qwen": qwen_segments},
        audio,
        pause_intervals_seconds=(),
        voice_activity_trace=None,
        voice_activity_offset_seconds=0.0,
        diarization=None,
        diarization_offset_seconds=0.0,
    )


def test_call_falls_back_to_only_successful_source():
    """A single successful source should remain usable without an LLM query."""
    audio = AudioSegment.silent(duration=1_000)
    segments = [_get_segment("甲", 0.1, 0.4)]
    whisper = Mock(spec=Transcriber, return_value=segments)
    mimo = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    merger = Mock(spec=AlignedTranscriptionMergeProcessor)
    ctc_aligner = Mock(spec=CtcAligner)
    transcriber = _get_transcriber(
        merger=merger,
        ctc_aligner=ctc_aligner,
        sources={"whisper": whisper, "mimo": mimo},
    )

    output = transcriber(audio)

    assert output is segments
    merger.process.assert_not_called()
    ctc_aligner.assert_not_called()


def test_call_excludes_source_with_pathological_compression():
    """A repetitive source rejected by its compression signal should be omitted."""
    audio = AudioSegment.silent(duration=1_000)
    whisper = Mock(
        spec=Transcriber,
        return_value=[_get_segment("呀" * 100, 0.1, 0.4, compression_ratio=37.0)],
    )
    mimo_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    mimo = Mock(spec=Transcriber, return_value=mimo_segments)
    qwen = Mock(spec=Transcriber, return_value=qwen_segments)
    transcriber = _get_transcriber(
        sources={"whisper": whisper, "mimo": mimo, "qwen": qwen}
    )
    expected = [_get_segment("甲乙", 0.1, 0.5)]
    transcriber.merge = Mock(return_value=expected)

    output = transcriber(audio)

    assert output is expected
    transcriber.merge.assert_called_once_with(
        {"mimo": mimo_segments, "qwen": qwen_segments},
        audio,
        pause_intervals_seconds=(),
        voice_activity_trace=None,
        voice_activity_offset_seconds=0.0,
        diarization=None,
        diarization_offset_seconds=0.0,
    )
    assert transcriber.last_source_errors == {
        "whisper": "Segment 0 compression ratio 37.00 exceeds maximum 2.40."
    }


def test_call_excludes_source_with_timestamp_beyond_audio():
    """A source ending beyond the block tolerance should be omitted."""
    audio = AudioSegment.silent(duration=1_000)
    whisper = Mock(spec=Transcriber, return_value=[_get_segment("幻", 0.1, 2.1)])
    mimo_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    transcriber = _get_transcriber(
        sources={
            "whisper": whisper,
            "mimo": Mock(spec=Transcriber, return_value=mimo_segments),
            "qwen": Mock(spec=Transcriber, return_value=qwen_segments),
        }
    )
    expected = [_get_segment("甲乙", 0.1, 0.5)]
    transcriber.merge = Mock(return_value=expected)

    output = transcriber(audio)

    assert output is expected
    assert transcriber.last_source_errors == {
        "whisper": "Segment 0 ends at 2.10s beyond 1.00s source audio."
    }


def test_call_tolerates_one_source_inference_failure():
    """One backend failure should not discard other independently usable sources."""
    audio = AudioSegment.silent(duration=1_000)
    whisper_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    whisper = Mock(spec=Transcriber, return_value=whisper_segments)
    mimo = Mock(spec=Transcriber, side_effect=TranscriptionInferenceError("failed"))
    qwen = Mock(spec=Transcriber, return_value=qwen_segments)
    transcriber = _get_transcriber(
        sources={"whisper": whisper, "mimo": mimo, "qwen": qwen}
    )
    expected = [_get_segment("甲乙", 0.1, 0.5)]
    transcriber.merge = Mock(return_value=expected)

    output = transcriber(audio)

    assert output is expected
    assert transcriber.last_source_errors == {"mimo": "failed"}


def test_call_rejects_all_empty_sources():
    """No source output should become a conventional empty-transcription error."""
    empty = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    transcriber = _get_transcriber(sources={"whisper": empty, "mimo": empty})

    with raises(TranscriptionEmptyError, match="All transcription sources"):
        transcriber(AudioSegment.silent(duration=1_000))


def test_init_rejects_fewer_than_two_sources():
    """Multi-source construction should enforce its minimum source count."""
    with raises(ValueError, match="at least two sources"):
        _get_transcriber(sources={"whisper": Mock(spec=Transcriber)})


def test_merge_rejects_fewer_than_two_sources():
    """Direct merging should also enforce its minimum source count."""
    transcriber = _get_transcriber()

    with raises(ScinoephileError, match="at least two sources"):
        transcriber.merge(
            {"whisper": [_get_segment("甲", 0.1, 0.4)]},
            AudioSegment.silent(duration=1_000),
        )
