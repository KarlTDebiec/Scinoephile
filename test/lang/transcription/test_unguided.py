#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for unguided transcription orchestration and construction."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict
from unittest.mock import Mock, patch

import numpy as np
from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.diarization import (
    DiarizationMode,
    SpeakerDiarizationError,
    SpeakerDiarizationResult,
)
from scinoephile.audio.subtitles import (
    AudioSeries,
    UnguidedDelineationResult,
    UnguidedDelineator,
)
from scinoephile.audio.transcription import (
    DemucsMode,
    TranscribedSegment,
    TranscribedWord,
    Transcriber,
    VADImplementation,
    VADMode,
    VoiceActivityCache,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.audio.transcription.mlx_audio.backend import (
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.transcription.transcriber import TranscriptionBackend
from scinoephile.lang.transcription.unguided import (
    UnguidedTranscriber,
    get_unguided_transcriber,
)


def _get_result(segments: list[TranscribedSegment]) -> UnguidedDelineationResult:
    """Get a minimal successful delineation result.

    Arguments:
        segments: delineated transcription segments
    Returns:
        successful delineation result
    """
    return UnguidedDelineationResult(
        segments=segments, boundaries=[], total_cost=0.0, used_relaxed_constraints=False
    )


class _BlockVadKwargs(TypedDict):
    """Injected block-planning VAD dependencies."""

    block_vad_cache: VoiceActivityCache
    """Mocked full-source voice activity cache."""
    block_vad_detector: VoiceActivityDetector
    """Mocked full-source voice activity detector."""


def _get_block_vad_kwargs(
    duration_ms: int = 1_000, trace: VoiceActivityTrace | None = None
) -> _BlockVadKwargs:
    """Get mocked full-source block-planning VAD dependencies."""
    detector = Mock(spec=VoiceActivityDetector)
    detector.trace_cache_identity = {"implementation": "test"}
    cache = Mock(spec=VoiceActivityCache)
    if trace is None:
        trace = VoiceActivityTrace(
            np.zeros(1),
            start_ms=duration_ms / 2,
            step_ms=duration_ms,
            duration_ms=duration_ms,
        )
    cache.load.return_value = trace
    return {"block_vad_cache": cache, "block_vad_detector": detector}


def _get_segment(*, speaker: str | None = None) -> TranscribedSegment:
    """Get one timestamped transcription segment.

    Arguments:
        speaker: optional anonymous speaker label
    Returns:
        timestamped transcription segment
    """
    return TranscribedSegment(
        id=0,
        seek=0,
        start=0.1,
        end=0.6,
        text="你好",
        words=[
            TranscribedWord(
                text="你好", start=0.1, end=0.6, confidence=1.0, speaker=speaker
            )
        ],
    )


def test_process_transcribes_complete_audio_and_delineates():
    """Test processing sends complete audio through ASR and delineation."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    transcription_segments = [_get_segment()]
    delineated_segments = [_get_segment()]
    result = _get_result(delineated_segments)
    backend = Mock(spec=Transcriber, return_value=transcription_segments)
    delineator = Mock(spec=UnguidedDelineator, return_value=result)
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        delineator=delineator,
        **_get_block_vad_kwargs(),
    )

    output = transcriber.process(source)

    backend.assert_called_once_with(source.audio)
    delineator.assert_called_once()
    delineated_input = delineator.call_args.args[0]
    assert [
        (segment.start, segment.end, segment.text) for segment in delineated_input
    ] == [(0.1, 0.6, "你好")]
    assert transcriber.last_delineation_results == [result]
    assert transcriber.last_delineation_result is not None
    assert output.audio is source.audio
    assert [(event.start, event.end, event.text) for event in output] == [
        (100, 600, "你好")
    ]
    assert output.events[0].segment == delineated_segments[0]


def test_process_discards_blank_segments_before_delineation():
    """Test empty backend artifacts do not become unguided subtitles."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    blank_segment = _get_segment().model_copy(update={"text": "", "words": []})
    transcription_segment = _get_segment()
    backend = Mock(
        spec=Transcriber, return_value=[blank_segment, transcription_segment]
    )
    delineator = Mock(spec=UnguidedDelineator, side_effect=_get_result)
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        delineator=delineator,
        **_get_block_vad_kwargs(),
    )

    output = transcriber.process(source)

    delineator.assert_called_once()
    delineated_input = delineator.call_args.args[0]
    assert [segment.text for segment in delineated_input] == ["你好"]
    assert [event.text for event in output] == ["你好"]


def test_process_discards_blank_segments_created_by_delineation():
    """Test blank delineation artifacts do not become unguided subtitles."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    transcription_segment = _get_segment()
    blank_segment = _get_segment().model_copy(update={"text": "", "words": []})
    backend = Mock(spec=Transcriber, return_value=[transcription_segment])
    delineator = Mock(
        spec=UnguidedDelineator,
        return_value=_get_result([blank_segment, transcription_segment]),
    )
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        delineator=delineator,
        **_get_block_vad_kwargs(),
    )

    output = transcriber.process(source)

    assert [event.text for event in output] == ["你好"]


def test_process_wraps_invalid_delineation_as_domain_error():
    """Test malformed backend timing becomes a user-facing domain error."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    backend = Mock(spec=Transcriber, return_value=[_get_segment()])
    delineator = Mock(
        spec=UnguidedDelineator,
        side_effect=ValueError("Transcribed word timings are not ordered."),
    )
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        delineator=delineator,
        **_get_block_vad_kwargs(),
    )

    with raises(ScinoephileError, match="Unable to delineate unguided transcription"):
        transcriber.process(source)


def test_process_assigns_source_speakers_once_when_diarization_is_on():
    """Test required diarization assigns speakers before delineation once."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    transcription_segments = [_get_segment()]
    assigned_segments = [_get_segment(speaker="SPEAKER_00")]
    backend = Mock(spec=Transcriber, return_value=transcription_segments)
    diarization = Mock(spec=SpeakerDiarizationResult)
    diarization.assign_speakers.return_value = assigned_segments
    diarizer = Mock(return_value=diarization)
    delineator = Mock(
        spec=UnguidedDelineator, return_value=_get_result(assigned_segments)
    )
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        diarization_mode=DiarizationMode.ON,
        delineator=delineator,
        diarizer=diarizer,
        **_get_block_vad_kwargs(),
    )

    transcriber.process(source)

    diarizer.assert_called_once_with(source.audio)
    diarization.assign_speakers.assert_called_once_with(
        transcription_segments, offset_seconds=0.0
    )
    delineator.assert_called_once()


def test_process_continues_after_automatic_diarization_failure():
    """Test automatic diarization failure retains undiarized transcription."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    transcription_segments = [_get_segment()]
    backend = Mock(spec=Transcriber, return_value=transcription_segments)
    diarizer = Mock(side_effect=SpeakerDiarizationError("unavailable"))
    delineator = Mock(
        spec=UnguidedDelineator, return_value=_get_result(transcription_segments)
    )
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        diarization_mode=DiarizationMode.AUTO,
        delineator=delineator,
        diarizer=diarizer,
        **_get_block_vad_kwargs(),
    )

    output = transcriber.process(source)

    diarizer.assert_called_once_with(source.audio)
    delineator.assert_called_once()
    assert [event.text for event in output] == ["你好"]


def test_process_propagates_required_diarization_failure():
    """Test required diarization failure aborts before delineation."""
    source = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    backend = Mock(spec=Transcriber, return_value=[_get_segment()])
    error = SpeakerDiarizationError("unavailable")
    diarizer = Mock(side_effect=error)
    delineator = Mock(spec=UnguidedDelineator)
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        diarization_mode=DiarizationMode.ON,
        delineator=delineator,
        diarizer=diarizer,
        **_get_block_vad_kwargs(),
    )

    with raises(SpeakerDiarizationError) as exc_info:
        transcriber.process(source)

    assert exc_info.value is error
    diarizer.assert_called_once_with(source.audio)
    delineator.assert_not_called()


def test_process_transcribes_only_selected_padded_block_with_source_timings():
    """Selected blocks should retain only source-timed core words."""
    source = AudioSeries(audio=AudioSegment.silent(duration=12_000), events=[])
    trace = VoiceActivityTrace(
        np.asarray([0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
        start_ms=500,
        step_ms=1_000,
        duration_ms=12_000,
    )
    block_vad = _get_block_vad_kwargs(duration_ms=12_000, trace=trace)
    local_segment = TranscribedSegment(
        id=0,
        seek=0,
        start=1.2,
        end=1.6,
        text="第二段",
        words=[TranscribedWord(text="第二段", start=1.2, end=1.6, confidence=1.0)],
    )
    backend = Mock(spec=Transcriber, return_value=[local_segment])
    delineator = Mock(spec=UnguidedDelineator, side_effect=_get_result)
    transcriber = UnguidedTranscriber(
        language=Language.yue_hant,
        transcriber=backend,
        delineator=delineator,
        **block_vad,
    )

    output = transcriber.process(source, start_at_idx=1, stop_at_idx=2)

    assert len(backend.call_args.args[0]) == 9_000
    assert [(block.start_ms, block.end_ms) for block in transcriber.last_blocks] == [
        (0, 4_000),
        (4_000, 12_000),
    ]
    assert [(event.start, event.end, event.text) for event in output] == [
        (4_200, 4_600, "第二段")
    ]


def test_factory_selects_default_whisper_configuration(tmp_path: Path):
    """Test the factory selects language-specific Whisper defaults.

    Arguments:
        tmp_path: temporary cache root path
    """
    backend = Mock(spec=Transcriber)
    with (
        patch(
            "scinoephile.lang.transcription.unguided.WhisperTranscriber",
            return_value=backend,
        ) as whisper_transcriber_class,
        patch(
            "scinoephile.lang.transcription.unguided.MlxAudioTranscriber"
        ) as mlx_audio_transcriber_class,
    ):
        transcriber = get_unguided_transcriber(
            Language.yue_hant, cache_root_path=tmp_path
        )

    whisper_transcriber_class.assert_called_once_with(
        model_name="khleeloo/whisper-large-v3-cantonese",
        language="yue",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        vad_implementation=VADImplementation.SILERO,
        cache_root_path=tmp_path,
        overwrite_cache=False,
    )
    mlx_audio_transcriber_class.assert_not_called()
    assert transcriber.language is Language.yue_hant
    assert transcriber.transcriber is backend
    assert transcriber.diarization_mode is DiarizationMode.OFF


def test_factory_selects_mlx_audio_with_source_length_chunking(tmp_path: Path):
    """Test the factory configures MLX-Audio with thirty-second chunks.

    Arguments:
        tmp_path: temporary cache root path
    """
    backend = Mock(spec=Transcriber)
    with (
        patch(
            "scinoephile.lang.transcription.unguided.MlxAudioTranscriber",
            return_value=backend,
        ) as mlx_audio_transcriber_class,
        patch(
            "scinoephile.lang.transcription.unguided.WhisperTranscriber"
        ) as whisper_transcriber_class,
    ):
        transcriber = get_unguided_transcriber(
            Language.yue_hant,
            backend=TranscriptionBackend.MLX_AUDIO,
            mlx_audio_token_limit_guard=True,
            cache_root_path=tmp_path,
        )

    mlx_audio_transcriber_class.assert_called_once_with(
        model_name=MIMO_MODEL_NAME,
        language=Language.yue_hant,
        chunk_duration_seconds=30.0,
        token_limit_guard=True,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        vad_implementation=VADImplementation.SILERO,
        cache_root_path=tmp_path,
        overwrite_cache=False,
    )
    whisper_transcriber_class.assert_not_called()
    assert transcriber.language is Language.yue_hant
    assert transcriber.transcriber is backend


def test_factory_constructs_three_source_consensus_configuration(tmp_path: Path):
    """Test multi-source factory uses tested models and Whisper Pyannote VAD."""
    whisper = Mock(spec=Transcriber)
    mimo = Mock(spec=Transcriber)
    qwen = Mock(spec=Transcriber)
    composite = Mock()
    provider = Mock()
    with (
        patch(
            "scinoephile.lang.transcription.unguided.WhisperTranscriber",
            return_value=whisper,
        ) as whisper_transcriber_class,
        patch(
            "scinoephile.lang.transcription.unguided.MlxAudioTranscriber",
            side_effect=[mimo, qwen],
        ) as mlx_audio_transcriber_class,
        patch(
            "scinoephile.lang.transcription.unguided."
            "get_unguided_multi_source_transcriber",
            return_value=composite,
        ) as get_multi_source_transcriber,
    ):
        transcriber = get_unguided_transcriber(
            Language.yue_hant,
            multi_source=True,
            mlx_audio_token_limit_guard=True,
            cache_root_path=tmp_path,
            provider=provider,
            additional_context="人物名係阿明。",
        )

    whisper_transcriber_class.assert_called_once_with(
        model_name="khleeloo/whisper-large-v3-cantonese",
        language="yue",
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.ON,
        vad_implementation=VADImplementation.PYANNOTE,
        cache_root_path=tmp_path,
        overwrite_cache=False,
    )
    assert mlx_audio_transcriber_class.call_count == 2
    assert mlx_audio_transcriber_class.call_args_list[0].kwargs["model_name"] == (
        MIMO_MODEL_NAME
    )
    assert mlx_audio_transcriber_class.call_args_list[0].kwargs["token_limit_guard"]
    assert mlx_audio_transcriber_class.call_args_list[1].kwargs["model_name"] == (
        QWEN3_ASR_MODEL_NAME
    )
    assert not mlx_audio_transcriber_class.call_args_list[1].kwargs["token_limit_guard"]
    get_multi_source_transcriber.assert_called_once_with(
        Language.yue_hant,
        {"whisper": whisper, "mimo": mimo, "qwen": qwen},
        provider=provider,
        cache_root_path=tmp_path,
        overwrite_cache=False,
        additional_context="人物名係阿明。",
        no_op=False,
    )
    assert transcriber.transcriber is composite


def test_factory_rejects_model_override_with_multi_source():
    """Test one model override cannot ambiguously configure three sources."""
    with raises(ScinoephileError, match="single transcription model"):
        get_unguided_transcriber(
            Language.yue_hant, multi_source=True, model_name="custom/asr"
        )
