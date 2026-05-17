#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription tooling for written Cantonese/standard Chinese workflows.

Package hierarchy (modules may import from any above):
* deliniation / punctuation
* alignment
* aligner
* transcriber
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import MIMO_MODEL_NAME, MIMO_TOKENIZER_NAME
from scinoephile.core.llms import LLMProvider, OperationSpec, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_TRANSCRIPTION_DELINIATION_JSON_PATHS,
    YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_2_to_2 import Dual2To2Manager
from scinoephile.llms.providers.registry import get_provider

from .deliniation import YueDeliniationVsZhoPromptYueHans
from .punctuation import YuePunctuationVsZhoPromptYueHans, YueZhoPunctuationManager
from .transcriber import (
    DemucsMode,
    MimoRuntime,
    TranscriptionBackend,
    VADMode,
    YueTranscriber,
)

__all__ = [
    "YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC",
    "YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC",
    "get_yue_transcribed_vs_zho",
    "get_yue_vs_zho_transcriber",
    "DemucsMode",
    "MimoRuntime",
    "TranscriptionBackend",
    "VADMode",
    "YueTranscriber",
    "YueZhoTranscriberKwargs",
    "YueZhoTranscriptionKwargs",
]

YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-transcription-deliniation",
    test_case_table_name="test_cases__yue_zho__transcription_deliniation",
    manager_cls=Dual2To2Manager,
    prompt_cls=YueDeliniationVsZhoPromptYueHans,
)
"""Operation specification for written Cantonese transcription deliniation."""

YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-transcription-punctuation",
    test_case_table_name="test_cases__yue_zho__transcription_punctuation",
    manager_cls=YueZhoPunctuationManager,
    prompt_cls=YuePunctuationVsZhoPromptYueHans,
    list_fields={"query.yuewen_to_punctuate": 10},
)
"""Operation specification for written Cantonese transcription punctuation."""


class YueZhoTranscriptionKwargs(TypedDict, total=False):
    """Keyword arguments for get_yue_transcribed_vs_zho forwarding."""

    stop_at_idx: int | None
    """block index at which to stop processing, inclusive."""


class YueZhoTranscriberKwargs(TypedDict, total=False):
    """Keyword arguments for default YueTranscriber construction."""

    model_name: str
    """Whisper model name used for transcription."""
    backend: TranscriptionBackend
    """ASR backend used for initial transcription."""
    demucs_mode: DemucsMode
    """Demucs preprocessing mode for transcription."""
    vad_mode: VADMode
    """Whisper VAD mode for transcription."""
    mimo_model_name: str
    """MiMo model name used when backend is MiMo."""
    mimo_tokenizer_name: str
    """MiMo audio tokenizer name used when backend is MiMo."""
    mimo_runtime: MimoRuntime
    """Runtime implementation used for MiMo inference."""
    mimo_language: str
    """Language metadata passed to MiMo."""
    mimo_max_tokens: int | None
    """Optional maximum number of MiMo text tokens to generate."""
    mimo_chunk_duration_seconds: float | None
    """Optional chunk duration for MiMo inference."""
    mimo_chunk_overlap_seconds: float
    """Context overlap applied to each MiMo chunk."""
    mimo_worker_command: list[str] | tuple[str, ...] | None
    """Command that runs the MiMo worker."""
    mimo_aligner_backend: str
    """Timestamp alignment backend used when backend is MiMo."""
    mimo_aligner_language: str
    """Language code used by the MiMo timestamp aligner."""
    mimo_aligner_model_name: str | None
    """Optional timestamp aligner model name."""
    mimo_aligner_worker_command: list[str] | tuple[str, ...] | None
    """Command that runs the MiMo timestamp aligner worker."""
    mimo_fallback: bool
    """Whether Whisper and MiMo may fall back to each other."""
    provider: LLMProvider | None
    """provider to use for queries."""
    convert: OpenCCConfig | None
    """OpenCC configuration used for transcribed text conversion."""
    deliniation_prompt_cls: type[YueDeliniationVsZhoPromptYueHans]
    """prompt class used for alignment deliniation."""
    punctuation_prompt_cls: type[YuePunctuationVsZhoPromptYueHans]
    """prompt class used for transcription punctuation."""
    test_case_directory_path: Path | None
    """directory where encountered transcription test cases are persisted."""
    deliniation_test_cases: list[TestCase] | None
    """preloaded deliniation test cases used to seed the transcriber."""
    punctuation_test_cases: list[TestCase] | None
    """preloaded punctuation test cases used to seed the transcriber."""


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
    model_name: str = "khleeloo/whisper-large-v3-cantonese",
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.AUTO,
    mimo_model_name: str = MIMO_MODEL_NAME,
    mimo_tokenizer_name: str = MIMO_TOKENIZER_NAME,
    mimo_runtime: MimoRuntime = MimoRuntime.AUTO,
    mimo_language: str = "yue",
    mimo_max_tokens: int | None = None,
    mimo_chunk_duration_seconds: float | None = None,
    mimo_chunk_overlap_seconds: float = 1.0,
    mimo_worker_command: list[str] | tuple[str, ...] | None = None,
    mimo_aligner_backend: str = "whisperx",
    mimo_aligner_language: str = "zh",
    mimo_aligner_model_name: str | None = None,
    mimo_aligner_worker_command: list[str] | tuple[str, ...] | None = None,
    mimo_fallback: bool = True,
    provider: LLMProvider | None = None,
    convert: OpenCCConfig | None = None,
    additional_context: str | None = None,
    deliniation_prompt_cls: type[YueDeliniationVsZhoPromptYueHans] = (
        YueDeliniationVsZhoPromptYueHans
    ),
    punctuation_prompt_cls: type[YuePunctuationVsZhoPromptYueHans] = (
        YuePunctuationVsZhoPromptYueHans
    ),
    test_case_directory_path: Path | None = None,
    deliniation_test_cases: list[TestCase] | None = None,
    punctuation_test_cases: list[TestCase] | None = None,
) -> YueTranscriber:
    """Get YueTranscriber with default resources when available.

    Arguments:
        model_name: Whisper model name used for transcription
        backend: ASR backend used for initial transcription
        demucs_mode: Demucs preprocessing mode for transcription
        vad_mode: Whisper VAD mode for transcription
        mimo_model_name: MiMo model name used when backend is MiMo
        mimo_tokenizer_name: MiMo audio tokenizer name
        mimo_runtime: runtime implementation used for MiMo inference
        mimo_language: language metadata passed to MiMo
        mimo_max_tokens: optional maximum number of MiMo text tokens to generate
        mimo_chunk_duration_seconds: optional chunk duration for MiMo inference
        mimo_chunk_overlap_seconds: context overlap applied to each MiMo chunk
        mimo_worker_command: optional command that runs the MiMo worker
        mimo_aligner_backend: timestamp alignment backend for MiMo
        mimo_aligner_language: language code used by the MiMo timestamp aligner
        mimo_aligner_model_name: optional timestamp aligner model name
        mimo_aligner_worker_command: optional timestamp aligner worker command
        mimo_fallback: whether Whisper and MiMo may fall back to each other
        provider: provider to use for queries
        convert: OpenCC configuration used for transcribed text conversion
        additional_context: additional context to include in LLM prompts
        deliniation_prompt_cls: prompt class for alignment deliniation
        punctuation_prompt_cls: prompt class for transcription punctuation
        test_case_directory_path: optional directory where test cases are updated
        deliniation_test_cases: optional deliniation test cases
        punctuation_test_cases: optional punctuation test cases
    Returns:
        configured YueTranscriber
    """
    if provider is None:
        provider = get_provider()
    if test_case_directory_path is None:
        test_case_directory_path = _get_default_test_case_dir_path()
    if deliniation_test_cases is None:
        deliniation_test_cases = list(
            load_default_test_cases(
                Dual2To2Manager,
                deliniation_prompt_cls,
                YUE_ZHO_TRANSCRIPTION_DELINIATION_JSON_PATHS,
            )
        )
    if punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_default_test_cases(
                YueZhoPunctuationManager,
                punctuation_prompt_cls,
                YUE_ZHO_TRANSCRIPTION_PUNCTUATION_JSON_PATHS,
            )
        )
    return YueTranscriber(
        model_name=model_name,
        backend=backend,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        mimo_model_name=mimo_model_name,
        mimo_tokenizer_name=mimo_tokenizer_name,
        mimo_runtime=mimo_runtime,
        mimo_language=mimo_language,
        mimo_max_tokens=mimo_max_tokens,
        mimo_chunk_duration_seconds=mimo_chunk_duration_seconds,
        mimo_chunk_overlap_seconds=mimo_chunk_overlap_seconds,
        mimo_worker_command=mimo_worker_command,
        mimo_aligner_backend=mimo_aligner_backend,
        mimo_aligner_language=mimo_aligner_language,
        mimo_aligner_model_name=mimo_aligner_model_name,
        mimo_aligner_worker_command=mimo_aligner_worker_command,
        mimo_fallback=mimo_fallback,
        provider=provider,
        convert=convert,
        additional_context=additional_context,
        deliniation_prompt_cls=deliniation_prompt_cls,
        punctuation_prompt_cls=punctuation_prompt_cls,
        test_case_directory_path=test_case_directory_path,
        deliniation_test_cases=deliniation_test_cases,
        punctuation_test_cases=punctuation_test_cases,
    )


def _get_default_test_case_dir_path() -> Path:
    """Get the default writable test-case directory for transcription updates.

    Returns:
        writable runtime test-case root with transcription subdirectories present
    """
    test_case_dir_path = get_runtime_cache_dir_path("test_cases")
    (test_case_dir_path / "multilang/yue_zho/transcription/deliniation").mkdir(
        parents=True, exist_ok=True
    )
    (test_case_dir_path / "multilang/yue_zho/transcription/punctuation").mkdir(
        parents=True, exist_ok=True
    )
    return test_case_dir_path
