#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for reference-guided audio transcription."""

from __future__ import annotations

from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import get_guided_transcriber
from scinoephile.lang.transcription.processor import (
    DemucsMode,
    GuidedTranscriptionProcessor,
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
    demucs_mode: DemucsMode = DemucsMode.AUTO,
    vad_mode: VADMode = VADMode.AUTO,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    prune_test_cases: bool = False,
    delineation_prompt: DelineationPrompt | None = None,
    punctuation_prompt: PunctuationPrompt | None = None,
    delineation_json_path: Path | None = None,
    punctuation_json_path: Path | None = None,
    delineation_test_cases: list[TestCase] | None = None,
    punctuation_test_cases: list[TestCase] | None = None,
    transcriber: GuidedTranscriptionProcessor | None = None,
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
        demucs_mode: Demucs preprocessing mode
        vad_mode: Whisper VAD mode
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        prune_test_cases: whether to remove test cases not encountered in this run
        delineation_prompt: delineation prompt override
        punctuation_prompt: punctuation prompt override
        delineation_json_path: delineation test-case JSON file to load and update
        punctuation_json_path: punctuation test-case JSON file to load and update
        delineation_test_cases: preloaded delineation test cases
        punctuation_test_cases: preloaded punctuation test cases
        transcriber: guided transcription processor, or None to construct one
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
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
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
