#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for reference-guided audio transcription."""

from __future__ import annotations

from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADMode
from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import get_guided_transcriber
from scinoephile.lang.transcription.transcriber import (
    BlockDelineationMode,
    BlockPunctuationMode,
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionAlignmentMode,
    TranscriptionBackend,
)
from scinoephile.llms.block_delineation import BlockDelineationPrompt
from scinoephile.llms.block_punctuation import BlockPunctuationPrompt
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt

from .helpers import resolve_language

__all__ = ["transcribe_series_guided"]


def transcribe_series_guided(
    audio_series: AudioSeries,
    reference_series: Series,
    *,
    language: Language,
    guide_language: Language | None = None,
    model_name: str | None = None,
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.AUTO,
    vad_mode: VADMode = VADMode.AUTO,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    strip_generated_punctuation: bool = False,
    mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    alignment_mode: TranscriptionAlignmentMode = TranscriptionAlignmentMode.PAIRWISE,
    block_delineation_mode: BlockDelineationMode | None = None,
    block_punctuation_mode: BlockPunctuationMode | None = None,
    fallback_to_no_op: bool = False,
    prune_test_cases: bool = False,
    block_delineation_prompt: BlockDelineationPrompt | None = None,
    block_punctuation_prompt: BlockPunctuationPrompt | None = None,
    delineation_prompt: DelineationPrompt | None = None,
    punctuation_prompt: PunctuationPrompt | None = None,
    block_delineation_json_path: Path | None = None,
    block_punctuation_json_path: Path | None = None,
    delineation_json_path: Path | None = None,
    punctuation_json_path: Path | None = None,
    block_delineation_test_cases: list[TestCase] | None = None,
    block_punctuation_test_cases: list[TestCase] | None = None,
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
        model_name: backend-specific model override
        backend: audio transcription backend
        demucs_mode: Demucs preprocessing mode
        vad_mode: Whisper VAD mode
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        strip_generated_punctuation: whether to remove generated sentence
            punctuation after timing and before guided alignment
        mlx_audio_timing_mode: granularity of MLX-Audio CTC timing units
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        no_op: use neutral answers instead of querying an LLM
        alignment_mode: LLM query granularity for alignment and punctuation
        block_delineation_mode: block delineation strategy override
        block_punctuation_mode: block punctuation strategy override
        fallback_to_no_op: whether invalid block answers fall back to sparse no-op
        prune_test_cases: whether to remove test cases not encountered in this run
        block_delineation_prompt: block delineation prompt override
        block_punctuation_prompt: block punctuation prompt override
        delineation_prompt: delineation prompt override
        punctuation_prompt: punctuation prompt override
        block_delineation_json_path: block-delineation test-case JSON file
        block_punctuation_json_path: block-punctuation test-case JSON file
        delineation_json_path: delineation test-case JSON file to load and update
        punctuation_json_path: punctuation test-case JSON file to load and update
        block_delineation_test_cases: preloaded block-delineation test cases
        block_punctuation_test_cases: preloaded block-punctuation test cases
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
            model_name=model_name,
            backend=backend,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            strip_generated_punctuation=strip_generated_punctuation,
            mlx_audio_timing_mode=mlx_audio_timing_mode,
            provider=provider,
            additional_context=additional_context,
            no_op=no_op,
            alignment_mode=alignment_mode,
            block_delineation_mode=block_delineation_mode,
            block_punctuation_mode=block_punctuation_mode,
            fallback_to_no_op=fallback_to_no_op,
            prune_test_cases=prune_test_cases,
            block_delineation_prompt=block_delineation_prompt,
            block_punctuation_prompt=block_punctuation_prompt,
            delineation_prompt=delineation_prompt,
            punctuation_prompt=punctuation_prompt,
            block_delineation_json_path=block_delineation_json_path,
            block_punctuation_json_path=block_punctuation_json_path,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            block_delineation_test_cases=block_delineation_test_cases,
            block_punctuation_test_cases=block_punctuation_test_cases,
            delineation_test_cases=delineation_test_cases,
            punctuation_test_cases=punctuation_test_cases,
        )
    return transcriber.process(
        audio_series,
        reference_series,
        stop_at_idx=stop_at_idx,
        start_at_idx=start_at_idx,
    )
