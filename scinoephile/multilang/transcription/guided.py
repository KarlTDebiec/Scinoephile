#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and factory for reference-guided transcription."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.audio.transcription import get_segment_split_on_whitespace
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, Queryer, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.delineation import DelineationManager, DelineationPrompt
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.punctuation import PunctuationManager, PunctuationPrompt
from scinoephile.multilang.yue_zho.transcription import (
    DEFAULT_YUE_WHISPER_MODEL_NAME,
    YueDelineationVsZhoPromptYueHans,
    YueDelineationVsZhoPromptYueHant,
    YuePunctuationVsZhoPromptYueHans,
    YuePunctuationVsZhoPromptYueHant,
)

from .aligner import TranscriptionAligner
from .processor import (
    DemucsMode,
    GuidedTranscriptionProcessor,
    TranscribedSegmentSplitter,
    VADMode,
)

__all__ = [
    "DEFAULT_SPECS",
    "GuidedTranscriptionSpec",
    "get_guided_transcriber",
]


_YUE_ZHO_DELINEATION_JSON_PATHS = (
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

_YUE_ZHO_PUNCTUATION_JSON_PATHS = (
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


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidedTranscriptionSpec:
    """Configuration for one transcription/reference language pair."""

    model_name: str
    """Default Whisper model name."""
    whisper_language: str
    """Language code passed to Whisper."""
    delineation_prompt: DelineationPrompt
    """Prompt for moving transcription text between reference subtitles."""
    punctuation_prompt: PunctuationPrompt
    """Prompt for punctuating transcription text using a reference subtitle."""
    test_case_dir_path: Path
    """Relative runtime test-case directory path."""
    delineation_json_paths: tuple[Path, ...] = ()
    """Bundled delineation test-case JSON paths."""
    punctuation_json_paths: tuple[Path, ...] = ()
    """Bundled punctuation test-case JSON paths."""
    segment_splitter: TranscribedSegmentSplitter | None = None
    """Strategy for splitting raw Whisper segments."""


DEFAULT_SPECS: Mapping[
    tuple[Language, Language],
    GuidedTranscriptionSpec,
] = MappingProxyType(
    {
        (
            Language.yue_hans,
            Language.zho_hans,
        ): GuidedTranscriptionSpec(
            model_name=DEFAULT_YUE_WHISPER_MODEL_NAME,
            whisper_language="yue",
            delineation_prompt=YueDelineationVsZhoPromptYueHans,
            punctuation_prompt=YuePunctuationVsZhoPromptYueHans,
            test_case_dir_path=Path("multilang/yue_zho/transcription"),
            delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
            punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
            segment_splitter=get_segment_split_on_whitespace,
        ),
        (
            Language.yue_hans,
            Language.zho_hant,
        ): GuidedTranscriptionSpec(
            model_name=DEFAULT_YUE_WHISPER_MODEL_NAME,
            whisper_language="yue",
            delineation_prompt=YueDelineationVsZhoPromptYueHans,
            punctuation_prompt=YuePunctuationVsZhoPromptYueHans,
            test_case_dir_path=Path("multilang/yue_zho/transcription"),
            delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
            punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
            segment_splitter=get_segment_split_on_whitespace,
        ),
        (
            Language.yue_hant,
            Language.zho_hans,
        ): GuidedTranscriptionSpec(
            model_name=DEFAULT_YUE_WHISPER_MODEL_NAME,
            whisper_language="yue",
            delineation_prompt=YueDelineationVsZhoPromptYueHant,
            punctuation_prompt=YuePunctuationVsZhoPromptYueHant,
            test_case_dir_path=Path("multilang/yue_zho/transcription"),
            delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
            punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
            segment_splitter=get_segment_split_on_whitespace,
        ),
        (
            Language.yue_hant,
            Language.zho_hant,
        ): GuidedTranscriptionSpec(
            model_name=DEFAULT_YUE_WHISPER_MODEL_NAME,
            whisper_language="yue",
            delineation_prompt=YueDelineationVsZhoPromptYueHant,
            punctuation_prompt=YuePunctuationVsZhoPromptYueHant,
            test_case_dir_path=Path("multilang/yue_zho/transcription"),
            delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
            punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
            segment_splitter=get_segment_split_on_whitespace,
        ),
    }
)
"""Guided transcription specifications keyed by transcription and reference language."""


def get_guided_transcriber(
    language: Language,
    reference_language: Language,
    *,
    model_name: str | None = None,
    whisper_language: str | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.AUTO,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    delineation_prompt: DelineationPrompt | None = None,
    punctuation_prompt: PunctuationPrompt | None = None,
    test_case_dir_path: Path | None = None,
    delineation_test_cases: list[TestCase] | None = None,
    punctuation_test_cases: list[TestCase] | None = None,
    segment_splitter: TranscribedSegmentSplitter | None = None,
) -> GuidedTranscriptionProcessor:
    """Get a guided transcriber for a supported language pair.

    Arguments:
        language: transcription language
        reference_language: reference subtitle language
        model_name: Whisper model override
        whisper_language: Whisper language-code override
        demucs_mode: Demucs preprocessing mode
        vad_mode: Whisper VAD mode
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        delineation_prompt: delineation prompt override
        punctuation_prompt: punctuation prompt override
        test_case_dir_path: directory where encountered test cases are written
        delineation_test_cases: preloaded delineation test cases
        punctuation_test_cases: preloaded punctuation test cases
        segment_splitter: Whisper segment-splitting strategy override
    Returns:
        configured guided transcription processor
    Raises:
        ScinoephileError: if guided transcription does not support the language pair
    """
    key = (language, reference_language)
    if key not in DEFAULT_SPECS:
        raise ScinoephileError(
            "Guided transcription does not support language pair "
            f"{language.tag} <- {reference_language.tag}"
        )
    spec = DEFAULT_SPECS[key]

    if model_name is None:
        model_name = spec.model_name
    if whisper_language is None:
        whisper_language = spec.whisper_language
    if delineation_prompt is None:
        delineation_prompt = spec.delineation_prompt
    if punctuation_prompt is None:
        punctuation_prompt = spec.punctuation_prompt
    if segment_splitter is None:
        segment_splitter = spec.segment_splitter
    if test_case_dir_path is None:
        test_case_dir_path = get_runtime_cache_dir_path("test_cases")
        test_case_dir_path /= spec.test_case_dir_path
    (test_case_dir_path / "delineation").mkdir(parents=True, exist_ok=True)
    (test_case_dir_path / "punctuation").mkdir(parents=True, exist_ok=True)

    if delineation_test_cases is None:
        delineation_test_cases = list(
            load_default_test_cases(
                DelineationManager,
                delineation_prompt,
                spec.delineation_json_paths,
            )
        )
    if punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_default_test_cases(
                PunctuationManager,
                punctuation_prompt,
                spec.punctuation_json_paths,
            )
        )
    if provider is None:
        provider = get_provider()

    delineation_queryer = Queryer(
        DelineationManager.get_test_case_cls(delineation_prompt),
        verified_test_cases=[
            test_case for test_case in delineation_test_cases if test_case.verified
        ],
        provider=provider,
        cache_dir_path=get_runtime_cache_dir_path("llm"),
        additional_context=additional_context,
    )
    punctuation_queryer = Queryer(
        PunctuationManager.get_test_case_cls(punctuation_prompt),
        verified_test_cases=[
            test_case for test_case in punctuation_test_cases if test_case.verified
        ],
        provider=provider,
        cache_dir_path=get_runtime_cache_dir_path("llm"),
        additional_context=additional_context,
    )
    aligner = TranscriptionAligner(
        delineation_queryer=delineation_queryer,
        punctuation_queryer=punctuation_queryer,
        test_case_dir_path=test_case_dir_path,
    )
    return GuidedTranscriptionProcessor(
        language=language,
        reference_language=reference_language,
        model_name=model_name,
        whisper_language=whisper_language,
        aligner=aligner,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        segment_splitter=segment_splitter,
    )
