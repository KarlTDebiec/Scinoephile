#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-free multi-source transcription."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pytest import approx, raises

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column, Token
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
from scinoephile.lang.yue.transcription.token_similarity import YueTokenSimilarity
from scinoephile.llms.transcription import (
    TranscriptionAnswer,
    TranscriptionProcessor,
    TranscriptionRequestResult,
)
from scinoephile.workflows.multisource_transcription import MultiSourceTranscriber
from scinoephile.workflows.multisource_transcription.factory import (
    get_multi_source_transcriber,
)
from scinoephile.workflows.multisource_transcription.timing import (
    get_request_interval,
    get_timed_request_segments,
)


def _get_answer(*texts: str) -> TranscriptionAnswer:
    """Get one consensus answer from subtitle texts.

    Arguments:
        *texts: subtitle texts
    Returns:
        consensus answer containing subtitle boundaries
    """
    return TranscriptionAnswer(text="".join(f"{text}｜" for text in texts))


def _get_segment(
    text: str,
    start: float,
    end: float,
    *,
    compression_ratio: float | None = None,
    with_words: bool = True,
) -> TranscribedSegment:
    """Get one timestamped transcription segment.

    Arguments:
        text: transcribed text
        start: start time in seconds
        end: end time in seconds
        compression_ratio: optional backend quality signal
        with_words: whether to include word timing
    Returns:
        timestamped transcription segment
    """
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


def _get_transcriber(
    *,
    processor: TranscriptionProcessor | None = None,
    ctc_aligner: CtcAligner | None = None,
    sources: dict[str, Transcriber] | None = None,
) -> MultiSourceTranscriber:
    """Get a multi-source transcriber with mocked dependencies.

    Arguments:
        processor: optional consensus processor
        ctc_aligner: optional CTC aligner
        sources: optional named source transcribers
    Returns:
        configured multi-source transcriber
    """
    if processor is None:
        processor = Mock(spec=TranscriptionProcessor)
    if ctc_aligner is None:
        ctc_aligner = Mock(spec=CtcAligner)
    if sources is None:
        sources = {"whisper": Mock(spec=Transcriber), "mimo": Mock(spec=Transcriber)}
    return MultiSourceTranscriber(
        language=Language.yue_hant,
        transcribers=sources,
        aligner=Aligner(YueTokenSimilarity()),
        processor=processor,
        ctc_aligner=ctc_aligner,
    )


def test_merge_aligns_sources_and_preserves_consensus_subtitle_splits():
    """Test one request-level CTC pass retains consensus subtitle splits."""
    audio = AudioSegment.silent(duration=3_000)
    answer = _get_answer("甲", "乙")
    processor = Mock(spec=TranscriptionProcessor)
    processor.process_requests.return_value = (
        TranscriptionRequestResult(0, 2, answer),
    )
    ctc_aligner = Mock(spec=CtcAligner, return_value=[_get_segment("甲乙", 0.5, 2.5)])
    transcriber = _get_transcriber(processor=processor, ctc_aligner=ctc_aligner)

    output = transcriber.merge(
        {
            "whisper": [_get_segment("甲乙", 0.2, 2.2)],
            "mimo": [_get_segment("甲乙", 0.3, 2.3)],
        },
        audio,
    )

    assert [(segment.id, segment.text) for segment in output] == [(0, "甲"), (1, "乙")]
    assert [(segment.start, segment.end) for segment in output] == [
        (0.5, 1.5),
        (1.5, 2.5),
    ]
    assert transcriber.last_timing_sources == {0: "ctc-request", 1: "ctc-request"}
    ctc_aligner.assert_called_once_with(audio, "甲乙")
    sources, speaker = processor.process_requests.call_args.args
    assert [source.name for source in sources] == ["whisper", "mimo"]
    assert [source.text for source in sources] == ["甲乙", "甲乙"]
    assert speaker == "　　"


def test_merge_uses_long_pause_boundaries_as_separate_ctc_windows():
    """Test each request is aligned within its VAD-bounded audio span."""
    audio = AudioSegment.silent(duration=3_000)
    processor = Mock(spec=TranscriptionProcessor)
    processor.process_requests.return_value = (
        TranscriptionRequestResult(0, 1, _get_answer("甲")),
        TranscriptionRequestResult(5, 6, _get_answer("乙")),
    )
    ctc_aligner = Mock(
        spec=CtcAligner,
        side_effect=[[_get_segment("甲", 0.1, 0.4)], [_get_segment("乙", 0.2, 0.7)]],
    )
    transcriber = _get_transcriber(processor=processor, ctc_aligner=ctc_aligner)

    output = transcriber.merge(
        {
            "whisper": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.4)],
            "mimo": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.4)],
        },
        audio,
        pause_intervals_seconds=((0.5, 1.5),),
    )

    assert [(segment.start, segment.end, segment.text) for segment in output] == [
        (0.1, 0.4, "甲"),
        (1.7, 2.2, "乙"),
    ]
    assert [len(call.args[0]) for call in ctc_aligner.call_args_list] == [500, 1_500]


def test_merge_infers_pauses_when_explicit_evidence_is_unavailable():
    """Test absent VAD evidence falls back to shared source-timing gaps."""
    audio = AudioSegment.silent(duration=3_000)
    processor = Mock(spec=TranscriptionProcessor)
    processor.process_requests.return_value = (
        TranscriptionRequestResult(0, 1, _get_answer("甲")),
        TranscriptionRequestResult(6, 7, _get_answer("乙")),
    )
    ctc_aligner = Mock(
        spec=CtcAligner,
        side_effect=[[_get_segment("甲", 0.1, 0.3)], [_get_segment("乙", 0.1, 0.3)]],
    )
    transcriber = _get_transcriber(processor=processor, ctc_aligner=ctc_aligner)

    transcriber.merge(
        {
            "whisper": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.2)],
            "mimo": [_get_segment("甲", 0.1, 0.4), _get_segment("乙", 1.8, 2.2)],
        },
        audio,
    )

    assert transcriber.last_alignment is not None
    assert sum(column.is_pause for column in transcriber.last_alignment.columns) == 5
    assert [len(call.args[0]) for call in ctc_aligner.call_args_list] == [400, 1_200]


def test_timing_omits_empty_request_and_retains_later_consensus():
    """Test CTC timing skips empty request answers without losing later output."""
    audio = AudioSegment.silent(duration=3_000)
    ctc_aligner = Mock(spec=CtcAligner, return_value=[_get_segment("乙", 0.2, 0.7)])
    alignment = Alignment(
        source_names=("whisper", "mimo"),
        columns=(
            Column((Token("甲", 0.1, 0.4), Token("丙", 0.1, 0.4))),
            *(
                Column((None, None), pause_interval_seconds=(0.5, 1.5))
                for _ in range(4)
            ),
            Column((Token("乙", 1.8, 2.4), Token("乙", 1.8, 2.4))),
        ),
    )

    output, timing_sources = get_timed_request_segments(
        audio,
        alignment,
        (
            TranscriptionRequestResult(0, 1, TranscriptionAnswer(text="")),
            TranscriptionRequestResult(5, 6, _get_answer("乙")),
        ),
        ctc_aligner,
    )

    assert [(segment.text, segment.start, segment.end) for segment in output] == [
        ("乙", 1.7, 2.2)
    ]
    assert timing_sources == {0: "ctc-request"}
    ctc_aligner.assert_called_once()


def test_request_interval_falls_back_to_in_audio_lexical_timing():
    """Test invalid pause bounds fall back to usable lexical evidence."""
    alignment = Alignment(
        source_names=("whisper", "mimo"),
        columns=(
            Column((Token("甲", 0.1, 0.4), Token("甲", 0.1, 0.4))),
            Column((None, None), pause_interval_seconds=(1.2, 1.5)),
            Column((Token("乙", 0.6, 0.8), Token("乙", 0.6, 0.8))),
        ),
    )

    interval = get_request_interval(alignment, (2, 3), 1.0)

    assert interval == (0.35, 1.0)


def test_timing_retries_incomplete_request_against_unconsumed_block():
    """Test incomplete request timing retries against unconsumed block audio."""
    audio = AudioSegment.silent(duration=3_000)
    ctc_aligner = Mock(
        spec=CtcAligner,
        side_effect=[
            [_get_segment("甲", 0.1, 0.4)],
            TranscriptionAlignmentIncompleteError("incomplete"),
            [_get_segment("乙", 1.4, 2.0)],
            [_get_segment("丙", 0.1, 0.3)],
        ],
    )
    alignment = Alignment(
        source_names=("whisper", "mimo"),
        columns=(
            Column((Token("甲", 0.1, 0.4), Token("甲", 0.1, 0.4))),
            Column((None, None), pause_interval_seconds=(0.5, 1.5)),
            Column((Token("乙", 1.8, 2.4), Token("乙", 1.8, 2.4))),
            Column((None, None), pause_interval_seconds=(2.0, 2.1)),
            Column((Token("丙", 2.5, 2.8), Token("丙", 2.5, 2.8))),
        ),
    )

    output, timing_sources = get_timed_request_segments(
        audio,
        alignment,
        (
            TranscriptionRequestResult(0, 1, _get_answer("甲")),
            TranscriptionRequestResult(2, 3, _get_answer("乙")),
            TranscriptionRequestResult(4, 5, _get_answer("丙")),
        ),
        ctc_aligner,
    )

    assert [segment.text for segment in output] == ["甲", "乙", "丙"]
    assert [segment.start for segment in output] == approx([0.1, 1.8, 2.5])
    assert [segment.end for segment in output] == approx([0.4, 2.4, 2.7])
    assert timing_sources == {
        0: "ctc-request",
        1: "ctc-unconsumed-block",
        2: "ctc-request",
    }


def test_transcribe_block_runs_sources_and_merges_successful_outputs():
    """Test every source sees identical audio and usable evidence is merged."""
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
    for source in (whisper, mimo, qwen):
        source.assert_called_once()
        assert source.call_args.args == (audio,)
        assert callable(source.call_args.kwargs["is_usable"])
    transcriber.merge.assert_called_once_with(
        {"whisper": whisper_segments, "qwen": qwen_segments},
        audio,
        audio_events=None,
        diarization=None,
        language_identification=None,
        pause_intervals_seconds=None,
        source_offset_seconds=0.0,
        voice_activity_trace=None,
    )


def test_transcribe_block_falls_back_to_only_successful_source():
    """Test one successful source remains usable without a consensus query."""
    audio = AudioSegment.silent(duration=1_000)
    segments = [_get_segment("甲", 0.1, 0.4)]
    whisper = Mock(spec=Transcriber, return_value=segments)
    mimo = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    processor = Mock(spec=TranscriptionProcessor)
    ctc_aligner = Mock(spec=CtcAligner)
    transcriber = _get_transcriber(
        processor=processor,
        ctc_aligner=ctc_aligner,
        sources={"whisper": whisper, "mimo": mimo},
    )

    output = transcriber(audio)

    assert output is segments
    processor.process_requests.assert_not_called()
    ctc_aligner.assert_not_called()
    assert transcriber.last_lexical_alignment is not None


def test_transcribe_block_excludes_pathological_source():
    """Test source-level quality signals exclude unusable ASR evidence."""
    audio = AudioSegment.silent(duration=1_000)
    pathological_segments = [_get_segment("呀" * 100, 0.1, 0.4, compression_ratio=37.0)]

    def reject_pathological_segments(
        _audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment]:
        """Simulate a transcriber exhausting attempts after quality rejection."""
        assert is_usable is not None
        assert not is_usable(pathological_segments)
        return []

    rejected = Mock(spec=Transcriber, side_effect=reject_pathological_segments)
    mimo_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    transcriber = _get_transcriber(
        sources={
            "whisper": rejected,
            "mimo": Mock(spec=Transcriber, return_value=mimo_segments),
            "qwen": Mock(spec=Transcriber, return_value=qwen_segments),
        }
    )
    expected = [_get_segment("甲乙", 0.1, 0.5)]
    transcriber.merge = Mock(return_value=expected)

    output = transcriber(audio)

    assert output is expected
    assert transcriber.last_source_errors == {
        "whisper": "Segment 0 compression ratio 37.00 exceeds maximum 2.40."
    }


def test_transcribe_block_tolerates_source_inference_failure():
    """Test one backend failure does not discard other usable sources."""
    audio = AudioSegment.silent(duration=1_000)
    whisper_segments = [_get_segment("甲", 0.1, 0.4)]
    qwen_segments = [_get_segment("乙", 0.2, 0.5)]
    transcriber = _get_transcriber(
        sources={
            "whisper": Mock(spec=Transcriber, return_value=whisper_segments),
            "mimo": Mock(
                spec=Transcriber, side_effect=TranscriptionInferenceError("failed")
            ),
            "qwen": Mock(spec=Transcriber, return_value=qwen_segments),
        }
    )
    transcriber.merge = Mock(return_value=[_get_segment("甲乙", 0.1, 0.5)])

    transcriber(audio)

    assert transcriber.last_source_errors == {"mimo": "failed"}


def test_transcribe_block_rejects_all_empty_sources():
    """Test absent source output becomes an empty-transcription error."""
    empty = Mock(spec=Transcriber, side_effect=TranscriptionEmptyError("empty"))
    transcriber = _get_transcriber(sources={"whisper": empty, "mimo": empty})

    with raises(TranscriptionEmptyError, match="All transcription sources"):
        transcriber(AudioSegment.silent(duration=1_000))


def test_construction_and_direct_merge_enforce_source_count():
    """Test construction and direct merging require at least two sources."""
    with raises(ValueError, match="at least two sources"):
        _get_transcriber(sources={"whisper": Mock(spec=Transcriber)})

    transcriber = _get_transcriber()
    with raises(ScinoephileError, match="at least two sources"):
        transcriber.merge(
            {"whisper": [_get_segment("甲", 0.1, 0.4)]},
            AudioSegment.silent(duration=1_000),
        )


def test_factory_uses_current_language_transcription_processor():
    """Test factory composes the current language-level processor."""
    processor = Mock(spec=TranscriptionProcessor)
    sources = {"whisper": Mock(spec=Transcriber), "mimo": Mock(spec=Transcriber)}
    with patch(
        "scinoephile.workflows.multisource_transcription.factory.get_transcriber",
        return_value=processor,
    ) as get_processor:
        transcriber = get_multi_source_transcriber(
            Language.yue_hant, sources, shared_test_cases=[]
        )

    assert transcriber.processor is processor
    assert isinstance(transcriber.aligner.similarity, YueTokenSimilarity)
    get_processor.assert_called_once_with(
        Language.yue_hant,
        shared_test_cases=[],
        provider=None,
        cache_root_path=None,
        overwrite_cache=False,
        additional_context=None,
        current_test_cases_path=None,
        prune_test_cases=False,
    )
