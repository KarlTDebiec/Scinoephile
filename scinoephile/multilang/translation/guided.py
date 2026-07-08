#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided translation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core import Language
from scinoephile.core.llms import (
    LLMProvider,
    OperationSpec,
    ProcessorKwargs,
    TestCase,
)
from scinoephile.core.subtitles import Series
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
    DualNToMPrompt,
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

from .shared import DualNToMTranslationProcessorKwargs

__all__ = [
    "GUIDED_TRANSLATION_OPERATION_SPEC",
    "GuidedTranslationProcessKwargs",
    "GuidedTranslationProcessorKwargs",
    "get_guided_translated",
    "get_guided_translator",
]

GUIDED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="guided-translation",
    test_case_table_name="test_cases__guided_translation",
    manager_cls=DualNToMManager,
    prompt_cls=DualNToMPrompt,
)
"""Operation specification for guided translation."""

_ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()

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

_PROMPTS: dict[tuple[Language, Language], type[DualNToMPrompt]] = {
    (Language.yue_hans, Language.eng): EngYueGuidedTranslationPrompt,
    (Language.yue_hant, Language.eng): EngYueGuidedTranslationPrompt,
    (Language.zho_hans, Language.eng): EngZhoGuidedTranslationPrompt,
    (Language.zho_hant, Language.eng): EngZhoGuidedTranslationPrompt,
    (Language.eng, Language.yue_hans): YueEngGuidedTranslationPromptYueHans,
    (Language.eng, Language.yue_hant): YueEngGuidedTranslationPromptYueHant,
    (Language.zho_hans, Language.yue_hans): YueZhoGuidedTranslationPromptYueHans,
    (Language.zho_hant, Language.yue_hans): YueZhoGuidedTranslationPromptYueHans,
    (Language.zho_hans, Language.yue_hant): YueZhoGuidedTranslationPromptYueHant,
    (Language.zho_hant, Language.yue_hant): YueZhoGuidedTranslationPromptYueHant,
    (Language.eng, Language.zho_hans): ZhoEngGuidedTranslationPromptZhoHans,
    (Language.eng, Language.zho_hant): ZhoEngGuidedTranslationPromptZhoHant,
    (Language.yue_hans, Language.zho_hans): ZhoYueGuidedTranslationPromptZhoHans,
    (Language.yue_hant, Language.zho_hans): ZhoYueGuidedTranslationPromptZhoHans,
    (Language.yue_hans, Language.zho_hant): ZhoYueGuidedTranslationPromptZhoHant,
    (Language.yue_hant, Language.zho_hant): ZhoYueGuidedTranslationPromptZhoHant,
}
"""Guided translation prompts keyed by exact source and target languages."""


class GuidedTranslationProcessorKwargs(
    DualNToMTranslationProcessorKwargs,
    total=False,
):
    """Keyword arguments for guided translation processor initialization."""


class GuidedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for guided translation processing."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_guided_translated(
    source: Series,
    target: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNToMProcessor | None = None,
    **kwargs: Unpack[GuidedTranslationProcessKwargs],
) -> Series:
    """Translate subtitles using target-language guidance.

    Arguments:
        source: source-language subtitles to translate
        target: target-language guide subtitles
        source_language: source language
        target_language: target language
        translator: processor to use, or None to construct one
        **kwargs: translation process keyword arguments
    Returns:
        guided-translated subtitles
    """
    if translator is None:
        translator = get_guided_translator(source_language, target_language)
    return translator.process(source, target, **kwargs)


def get_guided_translator(
    source_language: Language,
    target_language: Language,
    prompt_cls: type[DualNToMPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> DualNToMProcessor:
    """Get a guided translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt_cls: prompt class override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured guided translation processor
    """
    if prompt_cls is None:
        prompt_cls = _PROMPTS[source_language, target_language]
    if test_cases is None:
        json_paths = _JSON_PATHS[source_language, target_language]
        test_cases = list(
            load_default_test_cases(DualNToMManager, prompt_cls, json_paths)
        )
    if provider is None:
        provider = get_provider()

    return DualNToMProcessor(prompt_cls, test_cases, provider=provider, **kwargs)
