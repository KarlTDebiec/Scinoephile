#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Standard translation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.eng_yue.translation import EngYueTranslationPrompt
from scinoephile.lang.eng_zho.translation import EngZhoTranslationPrompt
from scinoephile.lang.yue_eng.translation import (
    YueEngTranslationPromptYueHans,
    YueEngTranslationPromptYueHant,
)
from scinoephile.lang.yue_zho.translation import (
    YueZhoTranslationPromptYueHans,
    YueZhoTranslationPromptYueHant,
)
from scinoephile.lang.zho_eng.translation import (
    ZhoEngTranslationPromptZhoHans,
    ZhoEngTranslationPromptZhoHant,
)
from scinoephile.lang.zho_yue.translation import (
    ZhoYueTranslationPromptZhoHans,
    ZhoYueTranslationPromptZhoHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.translation import (
    TranslationManager,
    TranslationProcessor,
    TranslationPrompt,
)

__all__ = [
    "DEFAULT_PROMPTS",
    "get_translator",
]

_ENG_YUE_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-English regular translation JSON paths."""

_ENG_ZHO_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default standard Chinese-to-English regular translation JSON paths."""

_YUE_ENG_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-written Cantonese regular translation JSON paths."""

_YUE_ZHO_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default standard Chinese-to-written Cantonese regular translation JSON paths."""

_ZHO_ENG_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default English-to-standard Chinese regular translation JSON paths."""

_ZHO_YUE_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
"""Default written Cantonese-to-standard Chinese regular translation JSON paths."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.yue_hans, Language.eng): _ENG_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.eng): _ENG_YUE_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.eng): _ENG_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.eng): _ENG_ZHO_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hans): _YUE_ENG_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hant): _YUE_ENG_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hans): _YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hans): _YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hant): _YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hant): _YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hans): _ZHO_ENG_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hant): _ZHO_ENG_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hans): _ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hans): _ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): _ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): _ZHO_YUE_TRANSLATION_JSON_PATHS,
}
"""Regular translation JSON paths keyed by exact source and target languages."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], TranslationPrompt] = (
    MappingProxyType(
        {
            (Language.yue_hans, Language.eng): EngYueTranslationPrompt,
            (Language.yue_hant, Language.eng): EngYueTranslationPrompt,
            (Language.zho_hans, Language.eng): EngZhoTranslationPrompt,
            (Language.zho_hant, Language.eng): EngZhoTranslationPrompt,
            (Language.eng, Language.yue_hans): YueEngTranslationPromptYueHans,
            (Language.eng, Language.yue_hant): YueEngTranslationPromptYueHant,
            (Language.zho_hans, Language.yue_hans): YueZhoTranslationPromptYueHans,
            (Language.zho_hant, Language.yue_hans): YueZhoTranslationPromptYueHans,
            (Language.zho_hans, Language.yue_hant): YueZhoTranslationPromptYueHant,
            (Language.zho_hant, Language.yue_hant): YueZhoTranslationPromptYueHant,
            (Language.eng, Language.zho_hans): ZhoEngTranslationPromptZhoHans,
            (Language.eng, Language.zho_hant): ZhoEngTranslationPromptZhoHant,
            (Language.yue_hans, Language.zho_hans): ZhoYueTranslationPromptZhoHans,
            (Language.yue_hant, Language.zho_hans): ZhoYueTranslationPromptZhoHans,
            (Language.yue_hans, Language.zho_hant): ZhoYueTranslationPromptZhoHant,
            (Language.yue_hant, Language.zho_hant): ZhoYueTranslationPromptZhoHant,
        }
    )
)
"""Regular translation prompts keyed by exact source and target languages."""


def get_translator(
    source_language: Language,
    target_language: Language,
    prompt: TranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> TranslationProcessor:
    """Get a translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt: prompt override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured translation processor
    Raises:
        ScinoephileError: if translation does not support the language pair
    """
    key = (source_language, target_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Translation does not support language pair "
            f"{source_language.tag} -> {target_language.tag}"
        )

    if prompt is None:
        prompt = DEFAULT_PROMPTS[key]
    if test_cases is None:
        json_paths = _JSON_PATHS[key]
        test_cases = list(
            load_default_test_cases(TranslationManager, prompt, json_paths)
        )
    if provider is None:
        provider = get_provider()

    return TranslationProcessor(prompt, test_cases, provider=provider, **kwargs)
