#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and factory for reference-guided transcription."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.audio.transcription import (
    DemucsMode,
    MlxAudioTranscriber,
    VADMode,
    get_segment_split_on_whitespace,
)
from scinoephile.audio.transcription.mlx_audio.backend import MIMO_MODEL_NAME
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.ml import get_torch_device
from scinoephile.core.paths import get_runtime_data_root_path
from scinoephile.lang.yue_zho.transcription import (
    YueZhoAdvisoryBlockDelineationPromptYueHans,
    YueZhoAdvisoryBlockDelineationPromptYueHant,
    YueZhoBlockDelineationPromptYueHans,
    YueZhoBlockDelineationPromptYueHant,
    YueZhoBlockPunctuationPromptYueHans,
    YueZhoBlockPunctuationPromptYueHant,
    YueZhoCandidateBlockDelineationPromptYueHans,
    YueZhoCandidateBlockDelineationPromptYueHant,
    YueZhoDelineationPromptYueHans,
    YueZhoDelineationPromptYueHant,
    YueZhoPositionalBlockPunctuationPromptYueHans,
    YueZhoPositionalBlockPunctuationPromptYueHant,
    YueZhoPunctuationPromptYueHans,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms import load_shared_test_cases
from scinoephile.llms.block_delineation import (
    AdvisoryBlockDelineationManager,
    AdvisoryBlockDelineationProcessor,
    AdvisoryBlockDelineationPrompt,
    BlockDelineationManager,
    BlockDelineationProcessor,
    BlockDelineationPrompt,
    CandidateBlockDelineationManager,
    CandidateBlockDelineationProcessor,
    CandidateBlockDelineationPrompt,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationManager,
    BlockPunctuationProcessor,
    BlockPunctuationPrompt,
    PositionalBlockPunctuationManager,
    PositionalBlockPunctuationProcessor,
    PositionalBlockPunctuationPrompt,
)
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
from .block_aligner import BlockTranscriptionAligner
from .transcriber import (
    BlockDelineationMode,
    BlockPunctuationMode,
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscribedSegmentSplitter,
    TranscriptionAlignmentMode,
    TranscriptionBackend,
)

__all__ = [
    "DEFAULT_SPECS",
    "GuidedTranscriptionSpec",
    "TranscriptionLanguageSpec",
    "get_guided_transcriber",
]


_YUE_ZHO_DELINEATION_JSON_PATHS = (
    Path("kob/output/yue-Hant_transcribe/vad-auto/whisper/json/delineation-mps.json"),
    Path("kob/output/yue-Hant_transcribe/vad-auto/mimo/json/delineation-mps.json"),
    Path("kob/output/yue-Hant_transcribe/vad-auto/qwen/json/delineation-mps.json"),
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
    Path("kob/output/yue-Hant_transcribe/vad-auto/whisper/json/punctuation-mps.json"),
    Path("kob/output/yue-Hant_transcribe/vad-auto/mimo/json/punctuation-mps.json"),
    Path("kob/output/yue-Hant_transcribe/vad-auto/qwen/json/punctuation-mps.json"),
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

_YUE_ZHO_BLOCK_TEST_CASE_DIR_PATHS = tuple(
    Path(dataset_name)
    / "output"
    / "yue-Hant_transcribe"
    / vad_name
    / transcription_name
    / "json"
    for dataset_name in ("acoptc", "kob", "tmm")
    for vad_name in ("vad-auto", "vad-off")
    for transcription_name in ("whisper", "mimo", "qwen")
) + tuple(
    Path(dataset_name) / "output" / "yue-Hant_transcribe" / transcription_name / "json"
    for dataset_name in ("acopopb", "acoptc", "kob", "tmm")
    for transcription_name in ("whisper", "mimo", "qwen")
)
"""Repository JSON directories for each written Cantonese transcription run."""

_YUE_ZHO_CANDIDATE_BLOCK_TEST_CASE_DIR_PATHS = _YUE_ZHO_BLOCK_TEST_CASE_DIR_PATHS
"""Repository JSON directories for candidate/positional transcription runs."""

_YUE_ZHO_BLOCK_DELINEATION_JSON_PATHS = tuple(
    dir_path / "block_delineation-mps.json"
    for dir_path in _YUE_ZHO_BLOCK_TEST_CASE_DIR_PATHS
)
"""Repository block-delineation JSON paths for written Cantonese."""

_YUE_ZHO_BLOCK_PUNCTUATION_JSON_PATHS = tuple(
    dir_path / "block_punctuation-mps.json"
    for dir_path in _YUE_ZHO_BLOCK_TEST_CASE_DIR_PATHS
)
"""Repository block-punctuation JSON paths for written Cantonese."""

_YUE_ZHO_CANDIDATE_BLOCK_DELINEATION_JSON_PATHS = tuple(
    dir_path / "candidate_delineation-mps.json"
    for dir_path in _YUE_ZHO_CANDIDATE_BLOCK_TEST_CASE_DIR_PATHS
)
"""Repository candidate block-delineation JSON paths for written Cantonese."""

_YUE_ZHO_ADVISORY_BLOCK_DELINEATION_JSON_PATHS = tuple(
    Path(dataset_name)
    / "output"
    / "yue-Hant_transcribe"
    / transcription_name
    / "json"
    / "gated_advisory_delineation-mps.json"
    for dataset_name in ("acopopb", "acoptc", "kob", "tmm")
    for transcription_name in ("whisper", "mimo", "qwen")
)
"""Repository advisory block-delineation JSON paths for written Cantonese."""

_YUE_ZHO_POSITIONAL_BLOCK_PUNCTUATION_JSON_PATHS = tuple(
    dir_path / "positional_punctuation-mps.json"
    for dir_path in _YUE_ZHO_CANDIDATE_BLOCK_TEST_CASE_DIR_PATHS
)
"""Repository positional block-punctuation JSON paths for written Cantonese."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TranscriptionLanguageSpec:
    """Configuration for one transcription language."""

    model_names_by_backend: Mapping[TranscriptionBackend, str]
    """Default model names keyed by transcription backend."""
    whisper_language: str
    """Language code passed to Whisper."""
    segment_splitter: TranscribedSegmentSplitter | None = None
    """Strategy for splitting raw transcribed segments."""

    def get_model_name(self, backend: TranscriptionBackend) -> str:
        """Get the default model name for a transcription backend.

        Arguments:
            backend: audio transcription backend
        Returns:
            default model name for the backend
        Raises:
            ScinoephileError: if the backend has no configured default model
        """
        try:
            return self.model_names_by_backend[backend]
        except KeyError as exc:
            raise ScinoephileError(
                f"No default model is configured for transcription backend {backend}."
            ) from exc


_YUE_LANGUAGE_SPEC = TranscriptionLanguageSpec(
    model_names_by_backend=MappingProxyType(
        {
            TranscriptionBackend.MLX_AUDIO: MIMO_MODEL_NAME,
            TranscriptionBackend.WHISPER: "khleeloo/whisper-large-v3-cantonese",
        }
    ),
    whisper_language="yue",
    segment_splitter=get_segment_split_on_whitespace,
)
"""Transcription-language specification for written Cantonese."""


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidedTranscriptionSpec:
    """Configuration for one transcription/guide language pair."""

    language_spec: TranscriptionLanguageSpec
    """Configuration for the transcription language."""
    advisory_block_delineation_prompt: AdvisoryBlockDelineationPrompt
    """Prompt for unrestricted boundaries with advisory timing suggestions."""
    block_delineation_prompt: BlockDelineationPrompt
    """Prompt for moving target text across a complete guide block."""
    block_punctuation_prompt: BlockPunctuationPrompt
    """Prompt for punctuating target text across a complete guide block."""
    candidate_block_delineation_prompt: CandidateBlockDelineationPrompt
    """Prompt for selecting timing-supported target boundaries."""
    positional_block_punctuation_prompt: PositionalBlockPunctuationPrompt
    """Prompt for inserting punctuation at target character offsets."""
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
    block_delineation_json_paths: tuple[Path, ...] = ()
    """Bundled block-delineation test-case JSON paths."""
    block_punctuation_json_paths: tuple[Path, ...] = ()
    """Bundled block-punctuation test-case JSON paths."""
    advisory_block_delineation_json_paths: tuple[Path, ...] = ()
    """Bundled advisory block-delineation test-case JSON paths."""
    candidate_block_delineation_json_paths: tuple[Path, ...] = ()
    """Bundled candidate block-delineation test-case JSON paths."""
    positional_block_punctuation_json_paths: tuple[Path, ...] = ()
    """Bundled positional block-punctuation test-case JSON paths."""


_YUE_HANS_SPEC = GuidedTranscriptionSpec(
    language_spec=_YUE_LANGUAGE_SPEC,
    advisory_block_delineation_prompt=YueZhoAdvisoryBlockDelineationPromptYueHans,
    block_delineation_prompt=YueZhoBlockDelineationPromptYueHans,
    block_punctuation_prompt=YueZhoBlockPunctuationPromptYueHans,
    candidate_block_delineation_prompt=YueZhoCandidateBlockDelineationPromptYueHans,
    positional_block_punctuation_prompt=YueZhoPositionalBlockPunctuationPromptYueHans,
    delineation_prompt=YueZhoDelineationPromptYueHans,
    punctuation_prompt=YueZhoPunctuationPromptYueHans,
    test_case_dir_path=Path("lang/yue_zho/transcription"),
    block_delineation_json_paths=_YUE_ZHO_BLOCK_DELINEATION_JSON_PATHS,
    block_punctuation_json_paths=_YUE_ZHO_BLOCK_PUNCTUATION_JSON_PATHS,
    advisory_block_delineation_json_paths=(
        _YUE_ZHO_ADVISORY_BLOCK_DELINEATION_JSON_PATHS
    ),
    candidate_block_delineation_json_paths=(
        _YUE_ZHO_CANDIDATE_BLOCK_DELINEATION_JSON_PATHS
    ),
    positional_block_punctuation_json_paths=(
        _YUE_ZHO_POSITIONAL_BLOCK_PUNCTUATION_JSON_PATHS
    ),
    delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
    punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
)
"""Guided transcription specification for simplified written Cantonese."""

_YUE_HANT_SPEC = GuidedTranscriptionSpec(
    language_spec=_YUE_LANGUAGE_SPEC,
    advisory_block_delineation_prompt=YueZhoAdvisoryBlockDelineationPromptYueHant,
    block_delineation_prompt=YueZhoBlockDelineationPromptYueHant,
    block_punctuation_prompt=YueZhoBlockPunctuationPromptYueHant,
    candidate_block_delineation_prompt=YueZhoCandidateBlockDelineationPromptYueHant,
    positional_block_punctuation_prompt=YueZhoPositionalBlockPunctuationPromptYueHant,
    delineation_prompt=YueZhoDelineationPromptYueHant,
    punctuation_prompt=YueZhoPunctuationPromptYueHant,
    test_case_dir_path=Path("lang/yue_zho/transcription"),
    block_delineation_json_paths=_YUE_ZHO_BLOCK_DELINEATION_JSON_PATHS,
    block_punctuation_json_paths=_YUE_ZHO_BLOCK_PUNCTUATION_JSON_PATHS,
    advisory_block_delineation_json_paths=(
        _YUE_ZHO_ADVISORY_BLOCK_DELINEATION_JSON_PATHS
    ),
    candidate_block_delineation_json_paths=(
        _YUE_ZHO_CANDIDATE_BLOCK_DELINEATION_JSON_PATHS
    ),
    positional_block_punctuation_json_paths=(
        _YUE_ZHO_POSITIONAL_BLOCK_PUNCTUATION_JSON_PATHS
    ),
    delineation_json_paths=_YUE_ZHO_DELINEATION_JSON_PATHS,
    punctuation_json_paths=_YUE_ZHO_PUNCTUATION_JSON_PATHS,
)
"""Guided transcription specification for traditional written Cantonese."""


DEFAULT_SPECS: Mapping[tuple[Language, Language], GuidedTranscriptionSpec] = (
    MappingProxyType(
        {
            (Language.yue_hans, Language.zho_hans): _YUE_HANS_SPEC,
            (Language.yue_hans, Language.zho_hant): _YUE_HANS_SPEC,
            (Language.yue_hant, Language.zho_hans): _YUE_HANT_SPEC,
            (Language.yue_hant, Language.zho_hant): _YUE_HANT_SPEC,
        }
    )
)
"""Guided transcription specifications keyed by transcription and guide language."""


def get_guided_transcriber(
    language: Language,
    guide_language: Language,
    *,
    model_name: str | None = None,
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.AUTO,
    vad_mode: VADMode = VADMode.OFF,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    strip_generated_punctuation: bool = False,
    mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    punctuate: bool = True,
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
) -> GuidedTranscriber:
    """Get a guided transcriber for a supported language pair.

    Arguments:
        language: transcription language
        guide_language: guide subtitle language
        model_name: backend-specific model override
        backend: audio transcription backend
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        strip_generated_punctuation: whether to remove generated sentence
            punctuation after timing and before guided alignment
        mlx_audio_timing_mode: granularity of MLX-Audio CTC timing units
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        no_op: use neutral answers instead of querying an LLM
        punctuate: whether to query an LLM to punctuate delineated transcription
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
    Returns:
        configured guided transcriber
    Raises:
        ScinoephileError: if guided transcription does not support the language pair
    """
    key = (language, guide_language)
    if key not in DEFAULT_SPECS:
        raise ScinoephileError(
            "Guided transcription does not support language pair "
            f"{language.code} <- {guide_language.code}"
        )
    spec = DEFAULT_SPECS[key]
    language_spec = spec.language_spec

    if model_name is None:
        model_name = language_spec.get_model_name(backend)
    if provider is None:
        provider = get_provider()

    default_block_modes = {
        TranscriptionAlignmentMode.BLOCK: (
            BlockDelineationMode.GATED_ADVISORY,
            BlockPunctuationMode.FULL_TEXT,
        ),
        TranscriptionAlignmentMode.BLOCK_POSITIONAL: (
            BlockDelineationMode.CANDIDATE,
            BlockPunctuationMode.POSITIONAL,
        ),
    }
    if alignment_mode in default_block_modes:
        default_delineation_mode, default_punctuation_mode = default_block_modes[
            alignment_mode
        ]
        block_delineation_mode = block_delineation_mode or default_delineation_mode
        block_punctuation_mode = block_punctuation_mode or default_punctuation_mode
        aligner = _get_block_aligner(
            spec,
            provider,
            delineation_mode=block_delineation_mode,
            punctuation_mode=block_punctuation_mode,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            fallback_to_no_op=fallback_to_no_op,
            no_op=no_op,
            punctuate=punctuate,
            overwrite_cache=overwrite_cache,
            prune_test_cases=prune_test_cases,
            delineation_prompt=block_delineation_prompt,
            punctuation_prompt=block_punctuation_prompt,
            delineation_json_path=block_delineation_json_path,
            punctuation_json_path=block_punctuation_json_path,
            delineation_test_cases=block_delineation_test_cases,
            punctuation_test_cases=block_punctuation_test_cases,
        )
    else:
        if block_delineation_mode is not None or block_punctuation_mode is not None:
            raise ValueError("Block strategy overrides require a block alignment mode.")
        if fallback_to_no_op:
            raise ValueError(
                "fallback_to_no_op is supported only with block alignment modes."
            )
        aligner = _get_pairwise_aligner(
            spec,
            provider,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            no_op=no_op,
            punctuate=punctuate,
            overwrite_cache=overwrite_cache,
            prune_test_cases=prune_test_cases,
            delineation_prompt=delineation_prompt,
            punctuation_prompt=punctuation_prompt,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            delineation_test_cases=delineation_test_cases,
            punctuation_test_cases=punctuation_test_cases,
        )

    # Configure the selected audio transcription backend
    mlx_audio_transcriber = None
    if backend is TranscriptionBackend.MLX_AUDIO:
        mlx_audio_transcriber = MlxAudioTranscriber(
            model_name=model_name,
            language=language,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
        )
    if punctuate and block_punctuation_mode is BlockPunctuationMode.POSITIONAL:
        strip_generated_punctuation = True
    return GuidedTranscriber(
        language=language,
        guide_language=guide_language,
        model_name=model_name,
        whisper_language=language_spec.whisper_language,
        aligner=aligner,
        backend=backend,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        mlx_audio_transcriber=mlx_audio_transcriber,
        mlx_audio_timing_mode=mlx_audio_timing_mode,
        segment_splitter=language_spec.segment_splitter,
        strip_generated_punctuation=strip_generated_punctuation,
    )


def _get_block_aligner(
    spec: GuidedTranscriptionSpec,
    provider: LLMProvider,
    *,
    delineation_mode: BlockDelineationMode,
    punctuation_mode: BlockPunctuationMode,
    additional_context: str | None,
    cache_root_path: Path | None,
    fallback_to_no_op: bool,
    no_op: bool,
    punctuate: bool,
    overwrite_cache: bool,
    prune_test_cases: bool,
    delineation_prompt: BlockDelineationPrompt | None,
    punctuation_prompt: BlockPunctuationPrompt | None,
    delineation_json_path: Path | None,
    punctuation_json_path: Path | None,
    delineation_test_cases: list[TestCase] | None,
    punctuation_test_cases: list[TestCase] | None,
) -> BlockTranscriptionAligner:
    """Configure a block transcription aligner.

    Arguments:
        spec: guided transcription specification
        provider: provider to use for LLM queries
        delineation_mode: selected block delineation strategy
        punctuation_mode: selected block punctuation strategy
        additional_context: additional context to include in LLM prompts
        cache_root_path: cache root directory path
        fallback_to_no_op: whether invalid answers fall back to sparse no-op
        no_op: use neutral answers instead of querying an LLM
        punctuate: whether to configure and run block punctuation queries
        overwrite_cache: whether to replace matching generated cache files
        prune_test_cases: whether to remove unencountered test cases
        delineation_prompt: block delineation prompt override
        punctuation_prompt: block punctuation prompt override
        delineation_json_path: block-delineation test-case JSON file
        punctuation_json_path: block-punctuation test-case JSON file
        delineation_test_cases: preloaded block-delineation test cases
        punctuation_test_cases: preloaded block-punctuation test cases
    Returns:
        configured block transcription aligner
    """
    advisory_modes = {
        BlockDelineationMode.ADVISORY,
        BlockDelineationMode.GATED_ADVISORY,
    }
    use_advisory_suggestions = delineation_mode in advisory_modes
    gate_advisory_suggestions = delineation_mode is BlockDelineationMode.GATED_ADVISORY
    use_candidates = delineation_mode is BlockDelineationMode.CANDIDATE
    use_positional = punctuate and punctuation_mode is BlockPunctuationMode.POSITIONAL
    delineation_prompts = {
        BlockDelineationMode.ADVISORY: spec.advisory_block_delineation_prompt,
        BlockDelineationMode.GATED_ADVISORY: (spec.advisory_block_delineation_prompt),
        BlockDelineationMode.UNRESTRICTED: spec.block_delineation_prompt,
        BlockDelineationMode.CANDIDATE: spec.candidate_block_delineation_prompt,
    }
    delineation_prompt = delineation_prompt or delineation_prompts[delineation_mode]
    punctuation_prompts = {
        BlockPunctuationMode.FULL_TEXT: spec.block_punctuation_prompt,
        BlockPunctuationMode.POSITIONAL: spec.positional_block_punctuation_prompt,
    }
    if punctuate:
        punctuation_prompt = punctuation_prompt or punctuation_prompts[punctuation_mode]
    if delineation_json_path is None or (punctuate and punctuation_json_path is None):
        runtime_test_case_dir_path = (
            get_runtime_data_root_path(create=False)
            / "test_cases"
            / spec.test_case_dir_path
        )
        device = get_torch_device()
        if delineation_json_path is None:
            delineation_dir_names = {
                BlockDelineationMode.ADVISORY: "advisory_block_delineation",
                BlockDelineationMode.GATED_ADVISORY: (
                    "gated_advisory_block_delineation"
                ),
                BlockDelineationMode.UNRESTRICTED: "block_delineation",
                BlockDelineationMode.CANDIDATE: "candidate_block_delineation",
            }
            delineation_json_path = (
                runtime_test_case_dir_path
                / delineation_dir_names[delineation_mode]
                / f"{device}.json"
            )
        if punctuate and punctuation_json_path is None:
            punctuation_dir_names = {
                BlockPunctuationMode.FULL_TEXT: "block_punctuation",
                BlockPunctuationMode.POSITIONAL: "positional_block_punctuation",
            }
            punctuation_json_path = (
                runtime_test_case_dir_path
                / punctuation_dir_names[punctuation_mode]
                / f"{device}.json"
            )
    if delineation_test_cases is None:
        delineation_managers = {
            BlockDelineationMode.ADVISORY: AdvisoryBlockDelineationManager,
            BlockDelineationMode.GATED_ADVISORY: AdvisoryBlockDelineationManager,
            BlockDelineationMode.UNRESTRICTED: BlockDelineationManager,
            BlockDelineationMode.CANDIDATE: CandidateBlockDelineationManager,
        }
        delineation_json_paths_by_mode = {
            BlockDelineationMode.ADVISORY: (spec.advisory_block_delineation_json_paths),
            BlockDelineationMode.GATED_ADVISORY: (
                spec.advisory_block_delineation_json_paths
            ),
            BlockDelineationMode.UNRESTRICTED: spec.block_delineation_json_paths,
            BlockDelineationMode.CANDIDATE: (
                spec.candidate_block_delineation_json_paths
            ),
        }
        delineation_test_cases = list(
            load_shared_test_cases(
                delineation_managers[delineation_mode],
                delineation_prompt,
                delineation_json_paths_by_mode[delineation_mode],
            )
        )
    if punctuate and punctuation_test_cases is None:
        punctuation_managers = {
            BlockPunctuationMode.FULL_TEXT: BlockPunctuationManager,
            BlockPunctuationMode.POSITIONAL: PositionalBlockPunctuationManager,
        }
        punctuation_json_paths_by_mode = {
            BlockPunctuationMode.FULL_TEXT: spec.block_punctuation_json_paths,
            BlockPunctuationMode.POSITIONAL: (
                spec.positional_block_punctuation_json_paths
            ),
        }
        punctuation_test_cases = list(
            load_shared_test_cases(
                punctuation_managers[punctuation_mode],
                punctuation_prompt,
                punctuation_json_paths_by_mode[punctuation_mode],
            )
        )
    delineation_processor_classes = {
        BlockDelineationMode.ADVISORY: AdvisoryBlockDelineationProcessor,
        BlockDelineationMode.GATED_ADVISORY: AdvisoryBlockDelineationProcessor,
        BlockDelineationMode.UNRESTRICTED: BlockDelineationProcessor,
        BlockDelineationMode.CANDIDATE: CandidateBlockDelineationProcessor,
    }
    delineation_prompt_classes = {
        BlockDelineationMode.ADVISORY: AdvisoryBlockDelineationPrompt,
        BlockDelineationMode.GATED_ADVISORY: AdvisoryBlockDelineationPrompt,
        BlockDelineationMode.UNRESTRICTED: BlockDelineationPrompt,
        BlockDelineationMode.CANDIDATE: CandidateBlockDelineationPrompt,
    }
    expected_delineation_prompt_cls = delineation_prompt_classes[delineation_mode]
    if not isinstance(delineation_prompt, expected_delineation_prompt_cls):
        raise TypeError(
            f"{delineation_mode.value.title()} block delineation requires a "
            f"{expected_delineation_prompt_cls.__name__}."
        )
    delineation_processor = delineation_processor_classes[delineation_mode](
        delineation_prompt,
        shared_test_cases=delineation_test_cases,
        current_test_cases_path=delineation_json_path,
        provider=provider,
        additional_context=additional_context,
        cache_root_path=cache_root_path,
        no_op=no_op,
        overwrite_cache=overwrite_cache,
        prune_test_cases=prune_test_cases,
    )
    punctuation_processor = None
    if use_positional:
        if not isinstance(punctuation_prompt, PositionalBlockPunctuationPrompt):
            raise TypeError(
                "Positional block punctuation requires a "
                "PositionalBlockPunctuationPrompt."
            )
        punctuation_processor = PositionalBlockPunctuationProcessor(
            punctuation_prompt,
            shared_test_cases=punctuation_test_cases,
            current_test_cases_path=punctuation_json_path,
            provider=provider,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            no_op=no_op,
            overwrite_cache=overwrite_cache,
            prune_test_cases=prune_test_cases,
        )
    elif punctuate:
        assert punctuation_prompt is not None
        punctuation_processor = BlockPunctuationProcessor(
            punctuation_prompt,
            shared_test_cases=punctuation_test_cases,
            current_test_cases_path=punctuation_json_path,
            provider=provider,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            no_op=no_op,
            overwrite_cache=overwrite_cache,
            prune_test_cases=prune_test_cases,
        )
    return BlockTranscriptionAligner(
        delineation_processor,
        punctuation_processor,
        fallback_to_no_op=fallback_to_no_op,
        gate_delineation_suggestions=gate_advisory_suggestions,
        use_delineation_candidates=use_candidates,
        use_delineation_suggestions=use_advisory_suggestions,
    )


def _get_pairwise_aligner(
    spec: GuidedTranscriptionSpec,
    provider: LLMProvider,
    *,
    additional_context: str | None,
    cache_root_path: Path | None,
    no_op: bool,
    punctuate: bool,
    overwrite_cache: bool,
    prune_test_cases: bool,
    delineation_prompt: DelineationPrompt | None,
    punctuation_prompt: PunctuationPrompt | None,
    delineation_json_path: Path | None,
    punctuation_json_path: Path | None,
    delineation_test_cases: list[TestCase] | None,
    punctuation_test_cases: list[TestCase] | None,
) -> TranscriptionAligner:
    """Configure a pairwise transcription aligner.

    Arguments:
        spec: guided transcription specification
        provider: provider to use for LLM queries
        additional_context: additional context to include in LLM prompts
        cache_root_path: cache root directory path
        no_op: use neutral answers instead of querying an LLM
        punctuate: whether to configure and run punctuation queries
        overwrite_cache: whether to replace matching generated cache files
        prune_test_cases: whether to remove unencountered test cases
        delineation_prompt: delineation prompt override
        punctuation_prompt: punctuation prompt override
        delineation_json_path: delineation test-case JSON file
        punctuation_json_path: punctuation test-case JSON file
        delineation_test_cases: preloaded delineation test cases
        punctuation_test_cases: preloaded punctuation test cases
    Returns:
        configured pairwise transcription aligner
    """
    if delineation_prompt is None:
        delineation_prompt = spec.delineation_prompt
    if punctuate and punctuation_prompt is None:
        punctuation_prompt = spec.punctuation_prompt
    if delineation_json_path is None or (punctuate and punctuation_json_path is None):
        runtime_test_case_dir_path = (
            get_runtime_data_root_path(create=False)
            / "test_cases"
            / spec.test_case_dir_path
        )
        device = get_torch_device()
        if delineation_json_path is None:
            delineation_json_path = (
                runtime_test_case_dir_path / "delineation" / f"{device}.json"
            )
        if punctuate and punctuation_json_path is None:
            punctuation_json_path = (
                runtime_test_case_dir_path / "punctuation" / f"{device}.json"
            )
    if delineation_test_cases is None:
        delineation_test_cases = list(
            load_shared_test_cases(
                DelineationManager, delineation_prompt, spec.delineation_json_paths
            )
        )
    if punctuate and punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_shared_test_cases(
                PunctuationManager, punctuation_prompt, spec.punctuation_json_paths
            )
        )
    delineation_processor = DelineationProcessor(
        delineation_prompt,
        shared_test_cases=delineation_test_cases,
        current_test_cases_path=delineation_json_path,
        provider=provider,
        additional_context=additional_context,
        cache_root_path=cache_root_path,
        no_op=no_op,
        overwrite_cache=overwrite_cache,
        prune_test_cases=prune_test_cases,
    )
    punctuation_processor = None
    if punctuate:
        assert punctuation_prompt is not None
        punctuation_processor = PunctuationProcessor(
            punctuation_prompt,
            shared_test_cases=punctuation_test_cases,
            current_test_cases_path=punctuation_json_path,
            provider=provider,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            no_op=no_op,
            overwrite_cache=overwrite_cache,
            prune_test_cases=prune_test_cases,
        )
    return TranscriptionAligner(
        delineation_processor=delineation_processor,
        punctuation_processor=punctuation_processor,
    )
