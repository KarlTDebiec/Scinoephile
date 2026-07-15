#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Gap translation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import (
    LLMProvider,
    ProcessorKwargs,
    TestCase,
)
from scinoephile.lang.eng_yue.translation import EngYueGapTranslationPrompt
from scinoephile.lang.eng_zho.translation import EngZhoGapTranslationPrompt
from scinoephile.lang.yue_eng.translation import (
    YueEngGapTranslationPromptYueHans,
    YueEngGapTranslationPromptYueHant,
)
from scinoephile.lang.yue_zho.translation import (
    YueZhoGapTranslationPromptYueHans,
    YueZhoGapTranslationPromptYueHant,
)
from scinoephile.lang.zho_eng.translation import (
    ZhoEngGapTranslationPromptZhoHans,
    ZhoEngGapTranslationPromptZhoHant,
)
from scinoephile.lang.zho_yue.translation import (
    ZhoYueGapTranslationPromptZhoHans,
    ZhoYueGapTranslationPromptZhoHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.gap_translation import (
    GapTranslationManager,
    GapTranslationProcessor,
    GapTranslationPrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = [
    "DEFAULT_PROMPTS",
    "get_gap_translator",
]

_ENG_YUE_GAP_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-English gap translation JSON paths."""

_ENG_ZHO_GAP_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default standard Chinese-to-English gap translation JSON paths."""

_YUE_ENG_GAP_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-written Cantonese gap translation JSON paths."""

_YUE_ZHO_GAP_TRANSLATION_JSON_PATHS = (
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/gap_translation/cuda.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/gap_translation/cpu.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/gap_translation/mps.json"),
)
"""Default standard Chinese-to-written Cantonese gap translation JSON paths."""

_ZHO_ENG_GAP_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-standard Chinese gap translation JSON paths."""

_ZHO_YUE_GAP_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-standard Chinese gap translation JSON paths."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.yue_hans, Language.eng): _ENG_YUE_GAP_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.eng): _ENG_YUE_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.eng): _ENG_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.eng): _ENG_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hans): _YUE_ENG_GAP_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hant): _YUE_ENG_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hans): _YUE_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hans): _YUE_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hant): _YUE_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hant): _YUE_ZHO_GAP_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hans): _ZHO_ENG_GAP_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hant): _ZHO_ENG_GAP_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hans): _ZHO_YUE_GAP_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hans): _ZHO_YUE_GAP_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): _ZHO_YUE_GAP_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): _ZHO_YUE_GAP_TRANSLATION_JSON_PATHS,
}
"""Gap translation JSON paths keyed by exact source and target languages."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], GapTranslationPrompt] = (
    MappingProxyType(
        {
            (Language.yue_hans, Language.eng): EngYueGapTranslationPrompt,
            (Language.yue_hant, Language.eng): EngYueGapTranslationPrompt,
            (Language.zho_hans, Language.eng): EngZhoGapTranslationPrompt,
            (Language.zho_hant, Language.eng): EngZhoGapTranslationPrompt,
            (Language.eng, Language.yue_hans): YueEngGapTranslationPromptYueHans,
            (Language.eng, Language.yue_hant): YueEngGapTranslationPromptYueHant,
            (Language.zho_hans, Language.yue_hans): YueZhoGapTranslationPromptYueHans,
            (Language.zho_hant, Language.yue_hans): YueZhoGapTranslationPromptYueHans,
            (Language.zho_hans, Language.yue_hant): YueZhoGapTranslationPromptYueHant,
            (Language.zho_hant, Language.yue_hant): YueZhoGapTranslationPromptYueHant,
            (Language.eng, Language.zho_hans): ZhoEngGapTranslationPromptZhoHans,
            (Language.eng, Language.zho_hant): ZhoEngGapTranslationPromptZhoHant,
            (Language.yue_hans, Language.zho_hans): ZhoYueGapTranslationPromptZhoHans,
            (Language.yue_hant, Language.zho_hans): ZhoYueGapTranslationPromptZhoHans,
            (Language.yue_hans, Language.zho_hant): ZhoYueGapTranslationPromptZhoHant,
            (Language.yue_hant, Language.zho_hant): ZhoYueGapTranslationPromptZhoHant,
        }
    )
)
"""Gap translation prompts keyed by exact source and target languages."""


def get_gap_translator(
    source_language: Language,
    target_language: Language,
    prompt: GapTranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> GapTranslationProcessor:
    """Get a gap translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt: prompt override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured gap translation processor
    Raises:
        ScinoephileError: if gap translation does not support the language pair
    """
    key = (source_language, target_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Gap translation does not support language pair "
            f"{source_language.code} -> {target_language.code}"
        )

    if prompt is None:
        prompt = DEFAULT_PROMPTS[key]
    if test_cases is None:
        json_paths = _JSON_PATHS[key]
        test_cases = list(
            load_default_test_cases(GapTranslationManager, prompt, json_paths)
        )
    if provider is None:
        provider = get_provider()

    return GapTranslationProcessor(prompt, test_cases, provider=provider, **kwargs)
