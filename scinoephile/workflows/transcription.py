#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for reference-guided audio transcription."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import (
    MIMO_MODEL_NAME,
    MimoRuntime,
)
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import get_guided_transcriber
from scinoephile.lang.transcription.transcriber import (
    DemucsMode,
    GuidedTranscriber,
    TranscriptionBackend,
    VADMode,
)
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt

from .helpers import resolve_language

__all__ = ["transcribe_series_guided"]


def transcribe_series_guided(
    audio_series: AudioSeries,
    reference_series: Series,
    *,
    language: Language,
    reference_language: Language | None = None,
    model_name: str | None = None,
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.AUTO,
    vad_mode: VADMode = VADMode.AUTO,
    mimo_model_name: str = MIMO_MODEL_NAME,
    mimo_runtime: MimoRuntime = MimoRuntime.AUTO,
    mimo_max_tokens: int | None = None,
    mimo_chunk_duration_seconds: float | None = None,
    mimo_chunk_overlap_seconds: float = 1.0,
    mimo_worker_command: Sequence[str] | None = None,
    mimo_aligner_backend: str = "ctc",
    mimo_aligner_model_name: str | None = None,
    mimo_aligner_worker_command: Sequence[str] | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
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
        reference_language: explicit reference language, or None to detect it
        model_name: Whisper model override
        backend: audio transcription backend
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        mimo_model_name: MiMo ASR model name or local path
        mimo_runtime: runtime implementation used for MiMo inference
        mimo_max_tokens: optional maximum number of MiMo tokens to generate
        mimo_chunk_duration_seconds: optional MiMo chunk duration in seconds
        mimo_chunk_overlap_seconds: context overlap applied to each MiMo chunk
        mimo_worker_command: optional subprocess command that runs MiMo
        mimo_aligner_backend: timestamp alignment backend for MiMo
        mimo_aligner_model_name: optional MiMo timestamp aligner model name
        mimo_aligner_worker_command: optional MiMo timestamp aligner worker command
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
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
        ScinoephileError: if the reference language cannot be resolved or the pair is
            unsupported
    """
    resolved_reference_language = resolve_language(
        reference_series,
        reference_language,
    )
    if transcriber is None:
        transcriber = get_guided_transcriber(
            language,
            resolved_reference_language,
            model_name=model_name,
            backend=backend,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            mimo_model_name=mimo_model_name,
            mimo_runtime=mimo_runtime,
            mimo_max_tokens=mimo_max_tokens,
            mimo_chunk_duration_seconds=mimo_chunk_duration_seconds,
            mimo_chunk_overlap_seconds=mimo_chunk_overlap_seconds,
            mimo_worker_command=mimo_worker_command,
            mimo_aligner_backend=mimo_aligner_backend,
            mimo_aligner_model_name=mimo_aligner_model_name,
            mimo_aligner_worker_command=mimo_aligner_worker_command,
            provider=provider,
            additional_context=additional_context,
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
