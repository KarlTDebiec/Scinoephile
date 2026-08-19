#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factory for complete reference-free transcription pipelines."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.transcription.artifact import TimingSettings
from scinoephile.audio.classification import (
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
)
from scinoephile.audio.diarization import PyannoteDiarizer
from scinoephile.audio.transcription.preprocessing_settings import DemucsMode
from scinoephile.audio.vad.cache import VoiceActivityCache
from scinoephile.audio.vad.detector import VoiceActivityDetector
from scinoephile.audio.vad.provider import VadImplementation
from scinoephile.audio.vad.speech_block import SpeechBlockSettings, SpeechBlockSplitter
from scinoephile.core.language import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.transcription.sources import (
    TranscriptionSourceSpec,
    get_transcription_sources,
)
from scinoephile.workflows.multisource_transcription.factory import (
    get_multi_source_transcriber,
)

from .pipeline import AudioAnalysisMode, TranscriptionPipeline

__all__ = ["get_transcription_pipeline"]


def get_transcription_pipeline(
    language: Language,
    *,
    audio_event_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
    source_specs: Sequence[TranscriptionSourceSpec] | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    diarization_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
    language_identification_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
    block_vad_implementation: VadImplementation = VadImplementation.PYANNOTE,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    current_test_cases_path: Path | None = None,
    prune_test_cases: bool = False,
    shared_test_cases: list[TestCase] | None = None,
    timing_settings: TimingSettings | None = None,
) -> TranscriptionPipeline:
    """Get a production aligned multi-source transcription pipeline.

    Arguments:
        language: transcription and output language
        audio_event_mode: source-wide speech, singing, and music mode
        source_specs: optional future-extensible ASR source registry override
        demucs_mode: source-level vocal-separation mode
        diarization_mode: source-wide speaker diarization mode
        language_identification_mode: source-wide spoken-language mode
        block_vad_implementation: VAD used for block planning
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        provider: provider to use for consensus queries
        additional_context: additional context for the consensus prompt
        no_op: use deterministic column consensus instead of an LLM
        current_test_cases_path: current transcription test-case JSON path
        prune_test_cases: whether to remove unencountered transcription test cases
        shared_test_cases: preloaded transcription test cases
        timing_settings: reference-free merged subtitle display timing
    Returns:
        configured production transcription pipeline
    """
    source_transcribers, alignment_sources = get_transcription_sources(
        language,
        source_specs=source_specs,
        demucs_mode=demucs_mode,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
    )
    transcriber = get_multi_source_transcriber(
        language,
        source_transcribers,
        provider=provider,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        additional_context=additional_context,
        no_op=no_op,
        current_test_cases_path=current_test_cases_path,
        prune_test_cases=prune_test_cases,
        shared_test_cases=shared_test_cases,
    )
    block_settings = SpeechBlockSettings()
    block_splitter = SpeechBlockSplitter(block_settings)
    block_vad_detector = VoiceActivityDetector(
        block_vad_implementation,
        threshold=block_settings.voice_activity_threshold,
        min_speech_duration_seconds=block_settings.min_speech_duration_seconds,
        min_silence_duration_seconds=0.0,
        padding_seconds=0.0,
    )
    audio_event_detector = None
    if audio_event_mode is not AudioAnalysisMode.OFF:
        audio_event_detector = FireRedAudioEventDetector(
            cache_root_path, overwrite_cache=overwrite_cache
        )
    diarizer = None
    if diarization_mode is not AudioAnalysisMode.OFF:
        diarizer = PyannoteDiarizer(cache_root_path, overwrite_cache=overwrite_cache)
    language_identifier = None
    if language_identification_mode is not AudioAnalysisMode.OFF:
        language_identifier = FireRedLanguageIdentifier(
            cache_root_path, overwrite_cache=overwrite_cache
        )
    return TranscriptionPipeline(
        language=language,
        transcriber=transcriber,
        alignment_sources=alignment_sources,
        block_splitter=block_splitter,
        block_vad_cache=VoiceActivityCache(cache_root_path, overwrite_cache),
        block_vad_detector=block_vad_detector,
        audio_event_mode=audio_event_mode,
        audio_event_detector=audio_event_detector,
        diarization_mode=diarization_mode,
        diarizer=diarizer,
        language_identification_mode=language_identification_mode,
        language_identifier=language_identifier,
        timing_settings=timing_settings,
    )
