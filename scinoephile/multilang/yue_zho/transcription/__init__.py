#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription tooling for written Cantonese/standard Chinese workflows.

Package hierarchy (modules may import from any above):
* delineation / punctuation
* alignment
* aligner
* transcriber
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.delineation import DelineationManager, DelineationPrompt
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.punctuation import PunctuationPrompt

from .delineation import YueDelineationVsZhoPromptYueHans
from .punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YueZhoPunctuationManager,
)
from .transcriber import (
    DEFAULT_YUE_WHISPER_MODEL_NAME,
    DemucsMode,
    VADMode,
    YueTranscriber,
)

__all__ = [
    "DEFAULT_YUE_WHISPER_MODEL_NAME",
    "get_yue_transcribed_vs_zho",
    "get_yue_vs_zho_transcriber",
    "DemucsMode",
    "VADMode",
    "YueTranscriber",
    "YueZhoTranscriberKwargs",
    "YueZhoTranscriptionKwargs",
]

_YUE_ZHO_TRANSCRIPTION_DELINEATION_JSON_PATHS = (
    Path(
        "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/"
        "delineation/cuda.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/"
        "delineation/mps.json"
    ),
)
"""Default written Cantonese transcription delineation JSON paths."""

_YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS = (
    Path(
        "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/"
        "punctuation/cuda.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/transcription/"
        "punctuation/mps.json"
    ),
)
"""Default written Cantonese transcription punctuation JSON paths."""


class YueZhoTranscriptionKwargs(TypedDict, total=False):
    """Keyword arguments for get_yue_transcribed_vs_zho forwarding."""

    stop_at_idx: int | None
    """block index at which to stop processing, inclusive."""


class YueZhoTranscriberKwargs(TypedDict, total=False):
    """Keyword arguments for default YueTranscriber construction."""

    model_name: str
    """Whisper model name used for transcription."""
    demucs_mode: DemucsMode
    """Demucs preprocessing mode for transcription."""
    vad_mode: VADMode
    """Whisper VAD mode for transcription."""
    provider: LLMProvider | None
    """provider to use for queries."""
    convert: OpenCCConfig | None
    """OpenCC configuration used for transcribed text conversion."""
    delineation_prompt: DelineationPrompt
    """prompt used for alignment delineation."""
    punctuation_prompt: PunctuationPrompt
    """prompt used for transcription punctuation."""
    test_case_directory_path: Path | None
    """directory where encountered transcription test cases are persisted."""
    delineation_test_cases: list[TestCase] | None
    """preloaded delineation test cases available to the transcriber."""
    punctuation_test_cases: list[TestCase] | None
    """preloaded punctuation test cases available to the transcriber."""


def get_yue_transcribed_vs_zho(
    yuewen: AudioSeries,
    zhongwen: Series,
    transcriber: YueTranscriber | None = None,
    convert: OpenCCConfig | None = None,
    **kwargs: Unpack[YueZhoTranscriptionKwargs],
) -> AudioSeries:
    """Get initial written Cantonese transcription aligned to standard Chinese.

    Arguments:
        yuewen: nascent written Cantonese audio subtitle series
        zhongwen: standard Chinese subtitle series
        transcriber: transcriber to use
        convert: OpenCC configuration used for transcribed text conversion
        **kwargs: additional keyword arguments for YueTranscriber.process_all_blocks
    Returns:
        transcribed written Cantonese subtitle series
    """
    if transcriber is None:
        transcriber = get_yue_vs_zho_transcriber(convert=convert)
    return transcriber.process_all_blocks(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_transcriber(
    model_name: str = DEFAULT_YUE_WHISPER_MODEL_NAME,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.AUTO,
    provider: LLMProvider | None = None,
    convert: OpenCCConfig | None = None,
    additional_context: str | None = None,
    delineation_prompt: DelineationPrompt = (YueDelineationVsZhoPromptYueHans),
    punctuation_prompt: PunctuationPrompt = (YuePunctuationVsZhoPromptYueHans),
    test_case_directory_path: Path | None = None,
    delineation_test_cases: list[TestCase] | None = None,
    punctuation_test_cases: list[TestCase] | None = None,
) -> YueTranscriber:
    """Get YueTranscriber with default resources when available.

    Arguments:
        model_name: Whisper model name used for transcription
        demucs_mode: Demucs preprocessing mode for transcription
        vad_mode: Whisper VAD mode for transcription
        provider: provider to use for queries
        convert: OpenCC configuration used for transcribed text conversion
        additional_context: additional context to include in LLM prompts
        delineation_prompt: prompt for alignment delineation
        punctuation_prompt: prompt for transcription punctuation
        test_case_directory_path: optional directory where test cases are updated
        delineation_test_cases: optional delineation test cases
        punctuation_test_cases: optional punctuation test cases
    Returns:
        configured YueTranscriber
    """
    if provider is None:
        provider = get_provider()
    if test_case_directory_path is None:
        test_case_directory_path = _get_default_test_case_dir_path()
    if delineation_test_cases is None:
        delineation_test_cases = list(
            load_default_test_cases(
                DelineationManager,
                delineation_prompt,
                _YUE_ZHO_TRANSCRIPTION_DELINEATION_JSON_PATHS,
            )
        )
    if punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_default_test_cases(
                YueZhoPunctuationManager,
                punctuation_prompt,
                _YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS,
            )
        )
    return YueTranscriber(
        model_name=model_name,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        provider=provider,
        convert=convert,
        additional_context=additional_context,
        delineation_prompt=delineation_prompt,
        punctuation_prompt=punctuation_prompt,
        test_case_directory_path=test_case_directory_path,
        delineation_test_cases=delineation_test_cases,
        punctuation_test_cases=punctuation_test_cases,
    )


def _get_default_test_case_dir_path() -> Path:
    """Get the default writable test-case directory for transcription updates.

    Returns:
        writable runtime test-case root with transcription subdirectories present
    """
    test_case_dir_path = get_runtime_cache_dir_path("test_cases")
    (test_case_dir_path / "multilang/yue_zho/transcription/delineation").mkdir(
        parents=True, exist_ok=True
    )
    (test_case_dir_path / "multilang/yue_zho/transcription/punctuation").mkdir(
        parents=True, exist_ok=True
    )
    return test_case_dir_path
