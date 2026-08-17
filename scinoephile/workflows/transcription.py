#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reusable audio transcription workflows."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.transcription import TimingSettings
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VadMode
from scinoephile.audio.vad import VadImplementation
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import get_guided_transcriber
from scinoephile.lang.transcription.sources import TranscriptionSourceSpec
from scinoephile.lang.transcription.transcriber import (
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionModel,
)
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt

from .helpers import resolve_language
from .transcription_pipeline import AudioAnalysisMode, TranscriptionPipeline
from .transcription_pipeline.factory import get_transcription_pipeline

__all__ = ["transcribe_series", "transcribe_series_guided"]


def transcribe_series(
    audio_series: AudioSeries,
    *,
    language: Language,
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
    alignment_outfile_path: Path | None = None,
    run_manifest_outfile_path: Path | None = None,
    prune_test_cases: bool = False,
    shared_test_cases: list[TestCase] | None = None,
    timing_settings: TimingSettings | None = None,
    pipeline: TranscriptionPipeline | None = None,
    exclude_blocks: Sequence[int] = (),
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
) -> AudioSeries:
    """Transcribe audio using aligned equal-status ASR evidence.

    Arguments:
        audio_series: complete source audio without required subtitle events
        language: transcription and output language
        audio_event_mode: source-wide speech, singing, and music mode
        source_specs: optional ASR source registry override
        demucs_mode: source-level vocal-separation mode
        diarization_mode: source-wide speaker diarization mode
        language_identification_mode: source-wide spoken-language mode
        block_vad_implementation: VAD used for block planning and pause evidence
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        provider: provider to use for consensus queries
        additional_context: additional context for the consensus prompt
        no_op: whether to use deterministic column consensus instead of an LLM
        current_test_cases_path: current transcription test-case JSON path
        alignment_outfile_path: portable alignment artifact output path
        run_manifest_outfile_path: current-run provenance manifest output path
        prune_test_cases: whether to remove unencountered transcription test cases
        shared_test_cases: preloaded transcription test cases
        timing_settings: reference-free merged subtitle display timing
        pipeline: optional preconfigured pipeline override
        exclude_blocks: one-based VAD block numbers to skip
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
            current_test_cases_path=current_test_cases_path,
            prune_test_cases=prune_test_cases,
            shared_test_cases=shared_test_cases,
            timing_settings=timing_settings,
        )
    output = pipeline.process(
        audio_series,
        exclude_blocks=exclude_blocks,
        start_at_idx=start_at_idx,
        stop_at_idx=stop_at_idx,
    )
    if alignment_outfile_path is not None:
        if pipeline.last_alignment_artifact is None:
            raise RuntimeError(
                "Transcription pipeline did not retain an alignment artifact."
            )
        pipeline.last_alignment_artifact.save(alignment_outfile_path)
    if run_manifest_outfile_path is not None:
        if pipeline.last_run_manifest is None:
            raise RuntimeError("Transcription pipeline did not retain a run manifest.")
        pipeline.last_run_manifest.save(run_manifest_outfile_path)
    return output


def transcribe_series_guided(
    audio_series: AudioSeries,
    reference_series: Series,
    *,
    language: Language,
    guide_language: Language | None = None,
    model: TranscriptionModel = TranscriptionModel.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VadMode = VadMode.OFF,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    strip_generated_punctuation: bool = False,
    mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
    mlx_audio_token_limit_guard: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    prune_test_cases: bool = False,
    delineation_prompt: DelineationPrompt | None = None,
    punctuation_prompt: PunctuationPrompt | None = None,
    delineation_json_path: Path | None = None,
    punctuation_json_path: Path | None = None,
    delineation_test_cases: list[TestCase] | None = None,
    punctuation_test_cases: list[TestCase] | None = None,
    transcriber: GuidedTranscriber | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
) -> AudioSeries:
    """Transcribe audio using reference subtitles.

    Arguments:
        audio_series: audio divided into subtitle-timed blocks
        reference_series: reference subtitles corresponding to audio blocks
        language: transcription language
        guide_language: explicit guide language, or None to detect it
        model: supported transcription model
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        strip_generated_punctuation: whether to remove generated sentence
            punctuation after timing and before guided alignment
        mlx_audio_timing_mode: granularity of MLX-Audio CTC timing units
        mlx_audio_token_limit_guard: whether to guard constrained MLX-Audio models
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        no_op: use neutral answers instead of querying an LLM
        prune_test_cases: whether to remove test cases not encountered in this run
        delineation_prompt: delineation prompt override
        punctuation_prompt: punctuation prompt override
        delineation_json_path: delineation test-case JSON file to load and update
        punctuation_json_path: punctuation test-case JSON file to load and update
        delineation_test_cases: preloaded delineation test cases
        punctuation_test_cases: preloaded punctuation test cases
        transcriber: guided transcriber, or None to construct one
        start_at_idx: inclusive zero-based block index at which to start processing
        stop_at_idx: exclusive zero-based block index at which to stop processing
    Returns:
        transcribed and reference-aligned audio subtitle series
    Raises:
        ScinoephileError: if the guide language cannot be resolved or the pair is
            unsupported
    """
    resolved_guide_language = resolve_language(reference_series, guide_language)
    if transcriber is None:
        transcriber = get_guided_transcriber(
            language,
            resolved_guide_language,
            model=model,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            strip_generated_punctuation=strip_generated_punctuation,
            mlx_audio_timing_mode=mlx_audio_timing_mode,
            mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
            provider=provider,
            additional_context=additional_context,
            no_op=no_op,
            prune_test_cases=prune_test_cases,
            delineation_prompt=delineation_prompt,
            punctuation_prompt=punctuation_prompt,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            delineation_test_cases=delineation_test_cases,
            punctuation_test_cases=punctuation_test_cases,
        )
    return transcriber.process(
        audio_series,
        reference_series,
        stop_at_idx=stop_at_idx,
        start_at_idx=start_at_idx,
    )
