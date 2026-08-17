#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for complete reference-free transcription orchestration."""

from __future__ import annotations

from logging import INFO
from typing import Literal, cast
from unittest.mock import Mock

import numpy as np
from pydantic import ValidationError
from pydub import AudioSegment
from pytest import LogCaptureFixture, MonkeyPatch, mark, raises

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column, Token
from scinoephile.analysis.transcription.artifact import AlignmentSource
from scinoephile.audio.classification import (
    AudioEvent,
    AudioEventDetectionResult,
    AudioEventSpan,
    LanguageIdentificationResult,
    LanguageSpan,
)
from scinoephile.audio.classification.exceptions import AudioClassificationError
from scinoephile.audio.diarization.exceptions import SpeakerDiarizationError
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import (
    TranscribedSegment,
    TranscribedWord,
    TranscriptionEmptyError,
)
from scinoephile.audio.vad import SpeechBlock, SpeechBlockSettings, VoiceActivityTrace
from scinoephile.core import Language
from scinoephile.lang.yue.transcription.token_similarity import YueTokenSimilarity
from scinoephile.workflows.transcription_pipeline import (
    AudioAnalysisMode,
    TranscriptionPipeline,
)
from scinoephile.workflows.transcription_pipeline import (
    factory as transcription_pipeline_factory,
)

_SOURCE_CACHE_KEY_SHA256S = {"one": "1" * 64, "two": "2" * 64}
"""Selected ASR cache keys used by the pipeline fixture."""
_QUERY_KEY_SHA256S = ("3" * 64,)
"""Semantic processor query keys used by the pipeline fixture."""


def _get_failed_analysis_pipeline(
    component: Literal["audio-event", "diarization", "language-identification"],
    mode: AudioAnalysisMode,
) -> tuple[TranscriptionPipeline, AudioSeries]:
    """Get a pipeline whose selected optional analysis raises a domain error.

    Arguments:
        component: optional analysis component that should fail
        mode: failure policy for the selected component
    Returns:
        configured pipeline and source audio
    """
    if component == "audio-event":
        detector = Mock(side_effect=AudioClassificationError("unavailable"))
        return _get_pipeline(audio_event_detector=detector, audio_event_mode=mode)
    if component == "diarization":
        diarizer = Mock(side_effect=SpeakerDiarizationError("unavailable"))
        return _get_pipeline(diarization_mode=mode, diarizer=diarizer)
    identifier = Mock(side_effect=AudioClassificationError("unavailable"))
    return _get_pipeline(
        language_identification_mode=mode, language_identifier=identifier
    )


def _get_pipeline(
    *,
    alignment_sources: tuple[AlignmentSource, ...] | None = None,
    audio_event_detector: Mock | None = None,
    audio_event_mode: AudioAnalysisMode = AudioAnalysisMode.OFF,
    diarization_mode: AudioAnalysisMode = AudioAnalysisMode.OFF,
    diarizer: Mock | None = None,
    language_identification_mode: AudioAnalysisMode = AudioAnalysisMode.OFF,
    language_identifier: Mock | None = None,
    segment: TranscribedSegment | None = None,
    transcription_error: TranscriptionEmptyError | None = None,
) -> tuple[TranscriptionPipeline, AudioSeries]:
    """Get a pipeline with deterministic mocked dependencies.

    Arguments:
        alignment_sources: optional portable source descriptors
        audio_event_detector: optional audio-event detector
        audio_event_mode: audio-event failure policy
        diarization_mode: diarization failure policy
        diarizer: optional speaker diarizer
        language_identification_mode: language-identification failure policy
        language_identifier: optional language identifier
        segment: optional transcription result
        transcription_error: optional transcription failure
    Returns:
        configured pipeline and source audio
    """
    audio = AudioSegment.silent(duration=1_000)
    audio_series = AudioSeries(audio)
    trace = VoiceActivityTrace(
        np.ones(10), start_ms=50.0, step_ms=100.0, duration_ms=1_000
    )
    block = SpeechBlock(
        index=0, start_ms=100, end_ms=900, buffered_start_ms=0, buffered_end_ms=1_000
    )
    block_splitter = Mock(return_value=[block])
    block_splitter.settings = SpeechBlockSettings(
        speech_free_gap_seconds=4.0, context_padding_seconds=0.75
    )
    block_vad_detector = Mock()
    block_vad_detector.cache_identity = {"implementation": "test"}
    block_vad_detector.trace_cache_identity = {"implementation": "test"}
    block_vad_detector.get_speech_intervals.return_value = [(100, 900)]
    block_vad_cache = Mock()
    block_vad_cache.load.return_value = trace

    if segment is None:
        word = TranscribedWord(text="甲", start=0.2004, end=0.4006, confidence=1.0)
        segment = TranscribedSegment(
            id=0, seek=0, start=0.2004, end=0.4006, text="甲", words=[word]
        )
    transcriber = Mock()
    transcriber.transcribers = {"one": Mock(), "two": Mock()}
    if transcription_error is None:
        transcriber.transcribe_block.return_value = [segment]
    else:
        transcriber.transcribe_block.side_effect = transcription_error
    transcriber.aligner = Aligner(YueTokenSimilarity())
    transcriber.last_lexical_alignment = Alignment(
        source_names=("one", "two"),
        columns=(
            Column(
                (
                    Token("甲", segment.start, segment.end),
                    Token("甲", segment.start, segment.end),
                )
            ),
        ),
    )
    transcriber.last_source_errors = {}
    transcriber.last_source_cache_key_sha256s = _SOURCE_CACHE_KEY_SHA256S
    transcriber.last_query_key_sha256s = _QUERY_KEY_SHA256S
    transcriber.last_timing_sources = {0: "source"}
    transcriber.processor.prune_test_cases = False
    transcriber.processor.test_case_cls.operation = "transcription"
    transcriber.processor.prompt.name = "test"
    transcriber.processor.queryer.provider.cache_identity = {"implementation": "test"}
    transcriber.processor.queryer.system_prompt = "test prompt"
    transcriber.processor.queryer.no_op = True

    if alignment_sources is None:
        alignment_sources = (
            AlignmentSource(name="one", backend="test", model="one"),
            AlignmentSource(name="two", backend="test", model="two"),
        )
    pipeline = TranscriptionPipeline(
        language=Language.yue_hant,
        transcriber=transcriber,
        alignment_sources=alignment_sources,
        audio_event_mode=audio_event_mode,
        audio_event_detector=audio_event_detector,
        diarization_mode=diarization_mode,
        diarizer=diarizer,
        language_identification_mode=language_identification_mode,
        language_identifier=language_identifier,
        block_splitter=block_splitter,
        block_vad_cache=block_vad_cache,
        block_vad_detector=block_vad_detector,
    )
    return pipeline, audio_series


def test_init_rejects_misaligned_source_descriptors():
    """Source descriptors should match transcriber names and order."""
    with raises(ValueError, match="must match transcription sources"):
        _get_pipeline(
            alignment_sources=(
                AlignmentSource(name="two", backend="test", model="two"),
                AlignmentSource(name="one", backend="test", model="one"),
            )
        )


def test_plan_blocks_saves_a_new_voice_activity_trace():
    """A cache miss should infer and save the reusable VAD trace."""
    pipeline, audio_series = _get_pipeline()
    block_vad_cache = cast(Mock, pipeline.block_vad_cache)
    block_vad_detector = cast(Mock, pipeline.block_vad_detector)
    trace = block_vad_cache.load.return_value
    block_vad_cache.load.return_value = None
    block_vad_detector.get_trace.return_value = trace

    blocks = pipeline.plan_blocks(audio_series)

    assert blocks == tuple(pipeline.last_blocks)
    block_vad_cache.save.assert_called_once_with(
        audio_series.audio, pipeline.block_vad_detector.trace_cache_identity, trace
    )


def test_plan_blocks_clears_stale_blocks_before_vad_failure():
    """A failed plan should not expose blocks from a previous source."""
    pipeline, audio_series = _get_pipeline()
    block_vad_cache = cast(Mock, pipeline.block_vad_cache)
    block_vad_cache.load.side_effect = RuntimeError("failed")

    with raises(RuntimeError, match="failed"):
        pipeline.plan_blocks(audio_series)

    assert not pipeline.last_blocks


def test_process_clears_stale_blocks_before_vad_failure():
    """A failed run should not expose blocks from a previous source."""
    pipeline, audio_series = _get_pipeline()
    block_vad_cache = cast(Mock, pipeline.block_vad_cache)
    block_vad_cache.load.side_effect = RuntimeError("failed")

    with raises(RuntimeError, match="failed"):
        pipeline.process(audio_series)

    assert not pipeline.last_blocks


def test_process_builds_subtitles_alignment_and_run_manifest(caplog: LogCaptureFixture):
    """One selected block should produce linked outputs and a completion log.

    Arguments:
        caplog: captured log records
    """
    pipeline, audio_series = _get_pipeline()
    caplog.set_level(
        INFO, logger="scinoephile.workflows.transcription_pipeline.pipeline"
    )

    output = pipeline.process(audio_series)

    transcribe_kwargs = cast(
        Mock, pipeline.transcriber
    ).transcribe_block.call_args.kwargs
    assert set(transcribe_kwargs) == {"diarization", "source_offset_seconds"}
    assert pipeline.last_alignment_artifact is not None
    assert pipeline.last_run_manifest is not None
    subtitle = pipeline.last_alignment_artifact.blocks[0].subtitles[0]
    assert [(event.start, event.end, event.text) for event in output.events] == [
        (subtitle.start_ms, subtitle.end_ms, "甲")
    ]
    assert subtitle.end_ms == 901
    assert pipeline.last_run_manifest.alignment_sha256 == (
        pipeline.last_alignment_artifact.sha256
    )
    assert pipeline.last_run_manifest.block_vad_identity == {
        "detector": {"implementation": "test"},
        "splitter": {
            "context_padding_seconds": 0.75,
            "min_silence_duration_seconds": 0.1,
            "min_speech_duration_seconds": 0.3,
            "speech_free_gap_seconds": 4.0,
            "voice_activity_threshold": 0.9,
        },
    }
    assert pipeline.last_run_manifest.blocks[0].source_cache_key_sha256s == (
        _SOURCE_CACHE_KEY_SHA256S
    )
    assert pipeline.last_run_manifest.blocks[0].query_key_sha256s == _QUERY_KEY_SHA256S
    assert pipeline.last_run_manifest.processor.no_op
    assert "BLOCK 1:" in caplog.text
    assert "TRANSCRIPTION (yue-Hant):" in caplog.text
    assert "甲" in caplog.text


def test_process_retains_audit_only_classifications_outside_transcriber_request():
    """Classification traces should reach the artifact but not consensus requests."""
    audio_events = AudioEventDetectionResult(
        spans=[
            AudioEventSpan(start=0.2, end=0.5, event=AudioEvent.MUSIC),
            AudioEventSpan(start=0.2, end=0.5, event=AudioEvent.SINGING),
        ]
    )
    languages = LanguageIdentificationResult(
        spans=[LanguageSpan(start=0.2, end=0.5, language="zh-yue", confidence=0.9)]
    )
    pipeline, audio_series = _get_pipeline(
        audio_event_detector=Mock(return_value=audio_events),
        audio_event_mode=AudioAnalysisMode.ON,
        language_identification_mode=AudioAnalysisMode.ON,
        language_identifier=Mock(return_value=languages),
    )

    pipeline.process(audio_series)

    transcribe_kwargs = cast(
        Mock, pipeline.transcriber
    ).transcribe_block.call_args.kwargs
    assert set(transcribe_kwargs) == {"diarization", "source_offset_seconds"}
    assert pipeline.last_alignment_artifact is not None
    block = pipeline.last_alignment_artifact.blocks[0]
    assert block.language_trace == "粵"
    assert block.singing_trace == "唱"
    assert block.music_trace == "樂"


def test_process_records_empty_transcription_blocks():
    """Empty transcription should produce a validated manifest record."""
    pipeline, audio_series = _get_pipeline(
        transcription_error=TranscriptionEmptyError("")
    )

    output = pipeline.process(audio_series)

    assert not output.events
    assert pipeline.last_run_manifest is not None
    assert pipeline.last_run_manifest.blocks[0].status == "empty"
    assert pipeline.last_run_manifest.blocks[0].reason == "TranscriptionEmptyError"


def test_process_excludes_configured_blocks(caplog: LogCaptureFixture):
    """Excluded one-based block numbers should skip transcription and be recorded.

    Arguments:
        caplog: captured log records
    """
    pipeline, audio_series = _get_pipeline()
    caplog.set_level(
        INFO, logger="scinoephile.workflows.transcription_pipeline.pipeline"
    )

    output = pipeline.process(audio_series, exclude_blocks=[1])

    assert not output.events
    transcriber = cast(Mock, pipeline.transcriber)
    transcriber.transcribe_block.assert_not_called()
    assert pipeline.last_alignment_artifact is not None
    assert not pipeline.last_alignment_artifact.blocks
    assert pipeline.last_run_manifest is not None
    assert pipeline.last_run_manifest.excluded_blocks == (1,)
    assert pipeline.last_run_manifest.blocks[0].status == "excluded"
    assert pipeline.last_run_manifest.blocks[0].reason == ("Excluded by configuration.")
    assert "Transcription block 1 is excluded." in caplog.text


@mark.parametrize("exclude_blocks", ([0], [2], [True], [1.0]))
def test_process_rejects_invalid_excluded_blocks(exclude_blocks: list[object]):
    """Block exclusions should contain valid one-based numbers from the plan.

    Arguments:
        exclude_blocks: invalid configured block exclusions
    """
    pipeline, audio_series = _get_pipeline()

    with raises(ValueError, match="Excluded transcription blocks"):
        pipeline.process(audio_series, exclude_blocks=cast(list[int], exclude_blocks))


def test_process_preserves_text_outside_the_vad_core():
    """Consensus text within the buffer should not be clipped to VAD activity."""
    word = TranscribedWord(text="甲", start=0.91, end=0.95, confidence=1.0)
    segment = TranscribedSegment(
        id=0, seek=0, start=0.91, end=0.95, text="甲", words=[word]
    )
    pipeline, audio_series = _get_pipeline(segment=segment)

    output = pipeline.process(audio_series)

    assert [event.text for event in output.events] == ["甲"]
    assert pipeline.last_alignment_artifact is not None
    subtitle = pipeline.last_alignment_artifact.blocks[0].subtitles[0]
    assert (subtitle.speech_start_ms, subtitle.speech_end_ms) == (910, 950)
    assert pipeline.last_run_manifest is not None
    assert pipeline.last_run_manifest.blocks[0].status == "transcribed"


def test_process_rejects_invalid_run_provenance():
    """Pipeline provenance should retain RunBlock digest validation."""
    pipeline, audio_series = _get_pipeline()
    pipeline.transcriber.last_query_key_sha256s = ("invalid",)

    with raises(ValidationError, match="query_key_sha256s"):
        pipeline.process(audio_series)


@mark.parametrize(
    "component", ("audio-event", "diarization", "language-identification")
)
def test_process_requires_enabled_audio_analysis(
    component: Literal["audio-event", "diarization", "language-identification"],
):
    """ON mode should propagate domain failures from every optional analysis.

    Arguments:
        component: optional analysis component that should fail
    """
    pipeline, audio_series = _get_failed_analysis_pipeline(
        component, AudioAnalysisMode.ON
    )

    with raises(
        (AudioClassificationError, SpeakerDiarizationError), match="unavailable"
    ):
        pipeline.process(audio_series)


@mark.parametrize(
    "component", ("audio-event", "diarization", "language-identification")
)
def test_process_tolerates_unavailable_audio_analysis(
    component: Literal["audio-event", "diarization", "language-identification"],
):
    """AUTO mode should tolerate domain failures from every optional analysis.

    Arguments:
        component: optional analysis component that should fail
    """
    pipeline, audio_series = _get_failed_analysis_pipeline(
        component, AudioAnalysisMode.AUTO
    )

    output = pipeline.process(audio_series)

    assert [event.text for event in output.events] == ["甲"]


def test_process_uses_selected_block_buffers_for_language_analysis():
    """Language analysis should inspect full selected buffers without VAD clipping."""
    audio_event_detector = Mock(return_value=None)
    language_identifier = Mock(return_value=None)
    pipeline, audio_series = _get_pipeline(
        audio_event_detector=audio_event_detector,
        audio_event_mode=AudioAnalysisMode.ON,
        language_identification_mode=AudioAnalysisMode.ON,
        language_identifier=language_identifier,
    )
    pipeline.last_blocks = []
    block_splitter = cast(Mock, pipeline.block_splitter)
    block_splitter.return_value = [
        SpeechBlock(
            index=0, start_ms=100, end_ms=400, buffered_start_ms=0, buffered_end_ms=500
        ),
        SpeechBlock(
            index=1,
            start_ms=600,
            end_ms=900,
            buffered_start_ms=500,
            buffered_end_ms=1_000,
        ),
    ]
    pipeline.process(audio_series, start_at_idx=1)

    audio_event_detector.assert_called_once_with(audio_series.audio)
    language_identifier.assert_called_once_with(audio_series.audio, ((500, 1_000),))


def test_factory_omits_disabled_audio_analysis(monkeypatch: MonkeyPatch):
    """Factory should omit optional analyzers and preserve source pairing."""
    source_transcribers = {"one": Mock(), "two": Mock()}
    alignment_sources = (
        AlignmentSource(name="one", backend="test", model="one"),
        AlignmentSource(name="two", backend="test", model="two"),
    )
    transcriber = Mock()
    pipeline = Mock()
    get_sources = Mock(return_value=(source_transcribers, alignment_sources))
    get_transcriber = Mock(return_value=transcriber)
    constructors = {
        "VoiceActivityDetector": Mock(),
        "VoiceActivityCache": Mock(),
        "FireRedAudioEventDetector": Mock(),
        "PyannoteDiarizer": Mock(),
        "FireRedLanguageIdentifier": Mock(),
    }
    get_pipeline = Mock(return_value=pipeline)
    monkeypatch.setattr(
        transcription_pipeline_factory, "get_transcription_sources", get_sources
    )
    monkeypatch.setattr(
        transcription_pipeline_factory, "get_multi_source_transcriber", get_transcriber
    )
    for name, constructor in constructors.items():
        monkeypatch.setattr(transcription_pipeline_factory, name, constructor)
    monkeypatch.setattr(
        transcription_pipeline_factory, "TranscriptionPipeline", get_pipeline
    )

    result = transcription_pipeline_factory.get_transcription_pipeline(
        Language.yue_hant,
        audio_event_mode=AudioAnalysisMode.OFF,
        diarization_mode=AudioAnalysisMode.OFF,
        language_identification_mode=AudioAnalysisMode.OFF,
    )

    assert result is pipeline
    constructors["FireRedAudioEventDetector"].assert_not_called()
    constructors["PyannoteDiarizer"].assert_not_called()
    constructors["FireRedLanguageIdentifier"].assert_not_called()
    pipeline_arguments = get_pipeline.call_args.kwargs
    assert pipeline_arguments["transcriber"] is transcriber
    assert pipeline_arguments["alignment_sources"] == alignment_sources
    assert pipeline_arguments["audio_event_detector"] is None
    assert pipeline_arguments["diarizer"] is None
    assert pipeline_arguments["language_identifier"] is None
