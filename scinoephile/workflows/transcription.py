#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reusable reference-free aligned multi-source transcription workflow."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis.transcription_alignment import SubtitleTimingSettings
from scinoephile.audio.classification import AudioClassificationMode
from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADImplementation
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.transcription.pipeline import (
    TranscriptionPipeline,
    get_transcription_pipeline,
)
from scinoephile.lang.transcription.sources import TranscriptionSourceSpec

__all__ = ["transcribe_series"]


def transcribe_series(
    audio_series: AudioSeries,
    *,
    language: Language,
    audio_event_mode: AudioClassificationMode = AudioClassificationMode.AUTO,
    source_specs: tuple[TranscriptionSourceSpec, ...] | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    diarization_mode: DiarizationMode = DiarizationMode.AUTO,
    language_identification_mode: AudioClassificationMode = (
        AudioClassificationMode.AUTO
    ),
    block_vad_implementation: VADImplementation = VADImplementation.PYANNOTE,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    aligned_merge_json_path: Path | None = None,
    alignment_json_path: Path | None = None,
    run_manifest_json_path: Path | None = None,
    prune_test_cases: bool = False,
    aligned_merge_test_cases: list[TestCase] | None = None,
    timing_settings: SubtitleTimingSettings | None = None,
    pipeline: TranscriptionPipeline | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
) -> AudioSeries:
    """Transcribe audio using aligned equal-status ASR evidence.

    Arguments:
        audio_series: complete source audio without required subtitle events
        language: transcription and output language
        audio_event_mode: source-wide speech, singing, and music mode
        source_specs: optional future-extensible ASR source registry override
        demucs_mode: source-level vocal-separation mode
        diarization_mode: source-wide speaker diarization mode
        language_identification_mode: source-wide spoken-language mode
        block_vad_implementation: VAD used for block planning and pause evidence
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        provider: provider to use for consensus queries
        additional_context: additional context for the consensus prompt
        no_op: select the first source instead of querying an LLM
        aligned_merge_json_path: aligned-merge test-case JSON path
        alignment_json_path: portable alignment artifact output path
        run_manifest_json_path: current-run provenance manifest output path
        prune_test_cases: whether to remove unencountered merge test cases
        aligned_merge_test_cases: preloaded aligned-merge test cases
        timing_settings: reference-free merged subtitle display timing
        pipeline: optional preconfigured pipeline override
        start_at_idx: inclusive zero-based VAD block index at which to start
        stop_at_idx: exclusive zero-based VAD block index at which to stop
    Returns:
        merged and timed audio subtitle series
    """
    if pipeline is None:
        pipeline = get_transcription_pipeline(
            language,
            audio_event_mode=audio_event_mode,
            source_specs=source_specs,
            demucs_mode=demucs_mode,
            diarization_mode=diarization_mode,
            language_identification_mode=language_identification_mode,
            block_vad_implementation=block_vad_implementation,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            provider=provider,
            additional_context=additional_context,
            no_op=no_op,
            aligned_merge_json_path=aligned_merge_json_path,
            prune_test_cases=prune_test_cases,
            aligned_merge_test_cases=aligned_merge_test_cases,
            timing_settings=timing_settings,
        )
    output = pipeline.process(
        audio_series, start_at_idx=start_at_idx, stop_at_idx=stop_at_idx
    )
    if alignment_json_path is not None:
        if pipeline.last_alignment_artifact is None:
            raise RuntimeError(
                "Transcription pipeline did not retain an alignment artifact."
            )
        pipeline.last_alignment_artifact.save(alignment_json_path)
    if run_manifest_json_path is not None:
        if pipeline.last_run_manifest is None:
            raise RuntimeError("Transcription pipeline did not retain a run manifest.")
        pipeline.last_run_manifest.save(run_manifest_json_path)
    return output
