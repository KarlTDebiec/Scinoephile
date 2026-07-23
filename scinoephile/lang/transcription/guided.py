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
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.ml import get_torch_device
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHans,
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHans,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.delineation import (
    DelineationManager,
    DelineationProcessor,
    DelineationPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.punctuation import (
    PunctuationManager,
    PunctuationProcessor,
    PunctuationPrompt,
)

from .aligner import TranscriptionAligner
from .transcriber import (
    DemucsMode,
    GuidedTranscriber,
    TranscribedSegmentSplitter,
    VADMode,
)

__all__ = [
    "DEFAULT_SPECS",
    "GuidedTranscriptionSpec",
    "TranscriptionLanguageSpec",
    "get_guided_transcriber",
]


_YUE_ZHO_DELINEATION_JSON_PATHS = (
    Path(
        "kob/output/yue-Hant_transcribe/lang/yue_zho/transcription/delineation/mps.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/transcription/"
        "delineation/cuda.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/transcription/"
        "delineation/mps.json"
    ),
)
"""Default written Cantonese transcription delineation JSON paths."""

_YUE_ZHO_PUNCTUATION_JSON_PATHS = (
    Path(
        "kob/output/yue-Hant_transcribe/lang/yue_zho/transcription/punctuation/mps.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/transcription/"
        "punctuation/cuda.json"
    ),
    Path(
        "mlamd/output/yue-Hans_transcribe/lang/yue_zho/transcription/"
        "punctuation/mps.json"
    ),
)
"""Default written Cantonese transcription punctuation JSON paths."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TranscriptionLanguageSpec:
    """Configuration for one transcription language."""

    model_name: str
    """Default Whisper model name."""
    whisper_language: str
    """Language code passed to Whisper."""
    segment_splitter: TranscribedSegmentSplitter | None = None
    """Strategy for splitting raw Whisper segments."""


_YUE_LANGUAGE_SPEC = TranscriptionLanguageSpec(
    model_name="khleeloo/whisper-large-v3-cantonese",
    whisper_language="yue",
    segment_splitter=get_segment_split_on_whitespace,
)
"""Transcription-language specification for written Cantonese."""


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidedTranscriptionSpec:
    """Configuration for one transcription/reference language pair."""

    language_spec: TranscriptionLanguageSpec
    """Configuration for the transcription language."""
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


_YUE_HANS_SPEC = GuidedTranscriptionSpec(
    language_spec=_YUE_LANGUAGE_SPEC,
    delineation_prompt=YueZhoDelineationPromptYueHans,
    punctuation_prompt=YueZhoPunctuationPromptYueHans,
    test_case_dir_path=Path("lang/yue_zho/transcription"),
    delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
    punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
)
"""Guided transcription specification for simplified written Cantonese."""

_YUE_HANT_SPEC = GuidedTranscriptionSpec(
    language_spec=_YUE_LANGUAGE_SPEC,
    delineation_prompt=YueZhoDelineationPromptYueHant,
    punctuation_prompt=YueZhoPunctuationPromptYueHant,
    test_case_dir_path=Path("lang/yue_zho/transcription"),
    delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
    punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
)
"""Guided transcription specification for traditional written Cantonese."""


DEFAULT_SPECS: Mapping[
    tuple[Language, Language],
    GuidedTranscriptionSpec,
] = MappingProxyType(
    {
        (
            Language.yue_hans,
            Language.zho_hans,
        ): _YUE_HANS_SPEC,
        (
            Language.yue_hans,
            Language.zho_hant,
        ): _YUE_HANS_SPEC,
        (
            Language.yue_hant,
            Language.zho_hans,
        ): _YUE_HANT_SPEC,
        (
            Language.yue_hant,
            Language.zho_hant,
        ): _YUE_HANT_SPEC,
    }
)
"""Guided transcription specifications keyed by transcription and reference language."""


def get_guided_transcriber(
    language: Language,
    reference_language: Language,
    *,
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
) -> GuidedTranscriber:
    """Get a guided transcriber for a supported language pair.

    Arguments:
        language: transcription language
        reference_language: reference subtitle language
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
    Returns:
        configured guided transcriber
    Raises:
        ScinoephileError: if guided transcription does not support the language pair
    """
    key = (language, reference_language)
    if key not in DEFAULT_SPECS:
        raise ScinoephileError(
            "Guided transcription does not support language pair "
            f"{language.code} <- {reference_language.code}"
        )
    spec = DEFAULT_SPECS[key]
    language_spec = spec.language_spec

    if model_name is None:
        model_name = language_spec.model_name
    if delineation_prompt is None:
        delineation_prompt = spec.delineation_prompt
    if punctuation_prompt is None:
        punctuation_prompt = spec.punctuation_prompt
    if delineation_json_path is None or punctuation_json_path is None:
        runtime_test_case_dir_path = (
            get_runtime_cache_dir_path("test_cases") / spec.test_case_dir_path
        )
        device = get_torch_device()
        if delineation_json_path is None:
            delineation_json_path = (
                runtime_test_case_dir_path / "delineation" / f"{device}.json"
            )
        if punctuation_json_path is None:
            punctuation_json_path = (
                runtime_test_case_dir_path / "punctuation" / f"{device}.json"
            )
    if delineation_test_cases is None:
        delineation_test_cases = list(
            load_default_test_cases(
                DelineationManager,
                delineation_prompt,
                spec.delineation_json_paths,
            )
        )
    if provider is None:
        provider = get_provider()
    delineation_processor = DelineationProcessor(
        delineation_prompt,
        test_cases=delineation_test_cases,
        test_case_path=delineation_json_path,
        provider=provider,
        additional_context=additional_context,
        prune_test_cases=prune_test_cases,
    )
    if punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_default_test_cases(
                PunctuationManager,
                punctuation_prompt,
                spec.punctuation_json_paths,
            )
        )
    punctuation_processor = PunctuationProcessor(
        punctuation_prompt,
        test_cases=punctuation_test_cases,
        test_case_path=punctuation_json_path,
        provider=provider,
        additional_context=additional_context,
        prune_test_cases=prune_test_cases,
    )
    aligner = TranscriptionAligner(
        delineation_processor=delineation_processor,
        punctuation_processor=punctuation_processor,
    )
    return GuidedTranscriber(
        language=language,
        reference_language=reference_language,
        model_name=model_name,
        whisper_language=language_spec.whisper_language,
        aligner=aligner,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        segment_splitter=language_spec.segment_splitter,
    )
