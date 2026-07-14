#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided translation helpers."""

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
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.guided_translation import (
    GuidedTranslationManager,
    GuidedTranslationProcessor,
    GuidedTranslationPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.translation import EngYueGuidedTranslationPrompt
from scinoephile.multilang.eng_zho.translation import EngZhoGuidedTranslationPrompt
from scinoephile.multilang.yue_eng.translation import (
    YueEngGuidedTranslationPromptYueHans,
    YueEngGuidedTranslationPromptYueHant,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoGuidedTranslationPromptYueHans,
    YueZhoGuidedTranslationPromptYueHant,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoEngGuidedTranslationPromptZhoHans,
    ZhoEngGuidedTranslationPromptZhoHant,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoYueGuidedTranslationPromptZhoHans,
    ZhoYueGuidedTranslationPromptZhoHant,
)

__all__ = [
    "DEFAULT_PROMPTS",
    "get_guided_translator",
]

_ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-English guided translation JSON paths."""

_ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default standard Chinese-to-English guided translation JSON paths."""

_YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-written Cantonese guided translation JSON paths."""

_YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default standard Chinese-to-written Cantonese guided translation JSON paths."""

_ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-standard Chinese guided translation JSON paths."""

_ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-standard Chinese guided translation JSON paths."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.yue_hans, Language.eng): _ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.eng): _ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.eng): _ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.eng): _ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hans): _YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hant): _YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hans): _YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hans): _YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hant): _YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hant): _YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hans): _ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hant): _ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hans): _ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hans): _ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): _ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): _ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
}
"""Guided translation JSON paths keyed by exact source and target languages."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], GuidedTranslationPrompt] = (
    MappingProxyType(
        {
            (Language.yue_hans, Language.eng): EngYueGuidedTranslationPrompt,
            (Language.yue_hant, Language.eng): EngYueGuidedTranslationPrompt,
            (Language.zho_hans, Language.eng): EngZhoGuidedTranslationPrompt,
            (Language.zho_hant, Language.eng): EngZhoGuidedTranslationPrompt,
            (Language.eng, Language.yue_hans): YueEngGuidedTranslationPromptYueHans,
            (Language.eng, Language.yue_hant): YueEngGuidedTranslationPromptYueHant,
            (
                Language.zho_hans,
                Language.yue_hans,
            ): YueZhoGuidedTranslationPromptYueHans,
            (
                Language.zho_hant,
                Language.yue_hans,
            ): YueZhoGuidedTranslationPromptYueHans,
            (
                Language.zho_hans,
                Language.yue_hant,
            ): YueZhoGuidedTranslationPromptYueHant,
            (
                Language.zho_hant,
                Language.yue_hant,
            ): YueZhoGuidedTranslationPromptYueHant,
            (Language.eng, Language.zho_hans): ZhoEngGuidedTranslationPromptZhoHans,
            (Language.eng, Language.zho_hant): ZhoEngGuidedTranslationPromptZhoHant,
            (
                Language.yue_hans,
                Language.zho_hans,
            ): ZhoYueGuidedTranslationPromptZhoHans,
            (
                Language.yue_hant,
                Language.zho_hans,
            ): ZhoYueGuidedTranslationPromptZhoHans,
            (
                Language.yue_hans,
                Language.zho_hant,
            ): ZhoYueGuidedTranslationPromptZhoHant,
            (
                Language.yue_hant,
                Language.zho_hant,
            ): ZhoYueGuidedTranslationPromptZhoHant,
        }
    )
)
"""Guided translation prompts keyed by exact source and target languages."""


def get_guided_translator(
    source_language: Language,
    target_language: Language,
    prompt: GuidedTranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> GuidedTranslationProcessor:
    """Get a guided translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt: prompt override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured guided translation processor
    Raises:
        ScinoephileError: if guided translation does not support the language pair
    """
    key = (source_language, target_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Guided translation does not support language pair "
            f"{source_language.tag} -> {target_language.tag}"
        )

    if prompt is None:
        prompt = DEFAULT_PROMPTS[key]
    if test_cases is None:
        json_paths = _JSON_PATHS[key]
        test_cases = list(
            load_default_test_cases(GuidedTranslationManager, prompt, json_paths)
        )
    if provider is None:
        provider = get_provider()

    return GuidedTranslationProcessor(prompt, test_cases, provider=provider, **kwargs)
