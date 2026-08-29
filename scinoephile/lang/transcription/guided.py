#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and factory for reference-guided transcription."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from scinoephile.audio.transcription import (
    CtcAligner,
    DemucsMode,
    MlxAudioModel,
    MlxAudioTranscriber,
    VadMode,
    get_segment_split_on_whitespace,
)
from scinoephile.audio.transcription.mlx_audio.model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from scinoephile.audio.transcription.whisper.model import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModel,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.ml import get_torch_device
from scinoephile.core.paths import get_runtime_data_root_path
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHans,
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHans,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms import load_shared_test_cases
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
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscribedSegmentSplitter,
    TranscriptionModel,
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

    models: Mapping[TranscriptionModel, WhisperModel | MlxAudioModelSpec]
    """Configured audio models keyed by supported transcription model."""
    segment_splitter: TranscribedSegmentSplitter | None = None
    """Strategy for splitting raw transcribed segments."""

    def get_model(self, model: TranscriptionModel) -> WhisperModel | MlxAudioModelSpec:
        """Get the configured audio model for a supported transcription model.

        Arguments:
            model: supported transcription model
        Returns:
            configured audio model
        Raises:
            ScinoephileError: if the transcription model is not configured
        """
        try:
            audio_model = self.models[model]
        except KeyError as exc:
            raise ScinoephileError(
                f"Transcription model {model} is not configured for this language."
            ) from exc
        return audio_model


_YUE_LANGUAGE_SPEC = TranscriptionLanguageSpec(
    models=MappingProxyType(
        {
            TranscriptionModel.WHISPER: WHISPER_LARGE_V3_CANTONESE_MODEL,
            TranscriptionModel.MIMO: MIMO_MODEL,
            TranscriptionModel.QWEN3_ASR: QWEN3_ASR_MODEL,
            TranscriptionModel.GLM_ASR: GLM_ASR_MODEL,
            TranscriptionModel.FIRERED_ASR2: FIRERED_ASR2_MODEL,
            TranscriptionModel.SENSEVOICE: SENSEVOICE_MODEL,
        }
    ),
    segment_splitter=get_segment_split_on_whitespace,
)
"""Transcription-language specification for written Cantonese."""


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidedTranscriptionSpec:
    """Configuration for one transcription/guide language pair."""

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
    model: TranscriptionModel = TranscriptionModel.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VadMode = VadMode.OFF,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    strip_generated_punctuation: bool = False,
    mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
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
) -> GuidedTranscriber:
    """Get a guided transcriber for a supported language pair.

    Arguments:
        language: transcription language
        guide_language: guide subtitle language
        model: supported transcription model
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
    key = (language, guide_language)
    if key not in DEFAULT_SPECS:
        raise ScinoephileError(
            "Guided transcription does not support language pair "
            f"{language.code} <- {guide_language.code}"
        )
    spec = DEFAULT_SPECS[key]
    language_spec = spec.language_spec

    audio_model = language_spec.get_model(model)
    if delineation_prompt is None:
        delineation_prompt = spec.delineation_prompt
    if punctuation_prompt is None:
        punctuation_prompt = spec.punctuation_prompt
    if delineation_json_path is None or punctuation_json_path is None:
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
        if punctuation_json_path is None:
            punctuation_json_path = (
                runtime_test_case_dir_path / "punctuation" / f"{device}.json"
            )
    if delineation_test_cases is None:
        delineation_test_cases = list(
            load_shared_test_cases(
                DelineationManager, delineation_prompt, spec.delineation_json_paths
            )
        )
    if provider is None:
        provider = get_provider()
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
    if punctuation_test_cases is None:
        punctuation_test_cases = list(
            load_shared_test_cases(
                PunctuationManager, punctuation_prompt, spec.punctuation_json_paths
            )
        )
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
    aligner = TranscriptionAligner(
        delineation_processor=delineation_processor,
        punctuation_processor=punctuation_processor,
    )

    # Configure the selected audio transcription backend
    mlx_audio_transcriber = None
    if isinstance(audio_model, MlxAudioModelSpec):
        mlx_audio_transcriber = MlxAudioTranscriber(
            model=MlxAudioModel(audio_model, language),
            ctc_aligner=CtcAligner(
                language,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            ),
            language=language,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
        )
    return GuidedTranscriber(
        language=language,
        guide_language=guide_language,
        audio_model=audio_model,
        aligner=aligner,
        demucs_mode=demucs_mode,
        vad_mode=vad_mode,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        mlx_audio_transcriber=mlx_audio_transcriber,
        mlx_audio_timing_mode=mlx_audio_timing_mode,
        segment_splitter=language_spec.segment_splitter,
        strip_generated_punctuation=strip_generated_punctuation,
    )
