#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and factory for reference-guided transcription."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.audio.transcription import (
    MIMO_MODEL_NAME,
    MimoRuntime,
    MimoTranscriber,
    get_segment_split_on_whitespace,
)
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
    TranscriptionBackend,
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
) -> GuidedTranscriber:
    """Get a guided transcriber for a supported language pair.

    Arguments:
        language: transcription language
        reference_language: reference subtitle language
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

    def _get_mimo_transcriber(
        *,
        use_demucs: bool,
        use_vad: bool,
    ) -> MimoTranscriber:
        """Build a MiMo transcriber for one Demucs cache identity.

        Arguments:
            use_demucs: whether Demucs preprocessing is represented in the cache key
            use_vad: whether to remove non-speech audio before MiMo inference
        Returns:
            configured MiMo transcriber
        """
        return MimoTranscriber(
            model_name=mimo_model_name,
            mimo_runtime=mimo_runtime,
            language=language,
            max_tokens=mimo_max_tokens,
            chunk_duration_seconds=mimo_chunk_duration_seconds,
            chunk_overlap_seconds=mimo_chunk_overlap_seconds,
            cache_dir_path=get_runtime_cache_dir_path("mimo"),
            aligner_backend=mimo_aligner_backend,
            aligner_model_name=mimo_aligner_model_name,
            aligner_worker_command=mimo_aligner_worker_command,
            worker_command=mimo_worker_command,
            use_demucs=use_demucs,
            use_vad=use_vad,
        )

    mimo_transcriber = None
    no_vad_mimo_transcriber = None
    unseparated_mimo_transcriber = None
    unseparated_no_vad_mimo_transcriber = None
    if backend == TranscriptionBackend.MIMO:
        mimo_transcriber = _get_mimo_transcriber(
            use_demucs=demucs_mode in (DemucsMode.AUTO, DemucsMode.ON),
            use_vad=vad_mode in (VADMode.AUTO, VADMode.ON),
        )
        no_vad_mimo_transcriber = (
            _get_mimo_transcriber(
                use_demucs=demucs_mode in (DemucsMode.AUTO, DemucsMode.ON),
                use_vad=False,
            )
            if vad_mode == VADMode.AUTO
            else None
        )
        unseparated_mimo_transcriber = (
            _get_mimo_transcriber(
                use_demucs=False,
                use_vad=vad_mode in (VADMode.AUTO, VADMode.ON),
            )
            if demucs_mode == DemucsMode.AUTO
            else None
        )
        unseparated_no_vad_mimo_transcriber = (
            _get_mimo_transcriber(
                use_demucs=False,
                use_vad=False,
            )
            if demucs_mode == DemucsMode.AUTO and vad_mode == VADMode.AUTO
            else None
        )
    return GuidedTranscriber(
        language=language,
        reference_language=reference_language,
        model_name=model_name,
        whisper_language=language_spec.whisper_language,
        aligner=aligner,
        backend=backend,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        mimo_transcriber=mimo_transcriber,
        no_vad_mimo_transcriber=no_vad_mimo_transcriber,
        unseparated_mimo_transcriber=unseparated_mimo_transcriber,
        unseparated_no_vad_mimo_transcriber=unseparated_no_vad_mimo_transcriber,
        segment_splitter=language_spec.segment_splitter,
    )
