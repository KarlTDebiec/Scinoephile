#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Standard translation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, OperationSpec, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.mono_n import MonoNManager, MonoNProcessor, MonoNPrompt
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.translation import EngYueTranslationPrompt
from scinoephile.multilang.eng_zho.translation import EngZhoTranslationPrompt
from scinoephile.multilang.yue_eng.translation import (
    YueEngTranslationPromptYueHans,
    YueEngTranslationPromptYueHant,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoTranslationPromptYueHans,
    YueZhoTranslationPromptYueHant,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoEngTranslationPromptZhoHans,
    ZhoEngTranslationPromptZhoHant,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoYueTranslationPromptZhoHans,
    ZhoYueTranslationPromptZhoHant,
)

from .shared import MonoNTranslationProcessorKwargs

__all__ = [
    "TRANSLATION_OPERATION_SPEC",
    "TranslationProcessKwargs",
    "TranslationProcessorKwargs",
    "get_translated",
    "get_translator",
]

TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="translation",
    test_case_table_name="test_cases__translation",
    manager_cls=MonoNManager,
    prompt_cls=MonoNPrompt,
)
"""Operation specification for regular translation."""

_ENG_YUE_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ENG_ZHO_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ENG_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ZHO_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ZHO_ENG_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ZHO_YUE_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()

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

_PROMPTS: dict[tuple[Language, Language], type[MonoNPrompt]] = {
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
"""Regular translation prompts keyed by exact source and target languages."""


class TranslationProcessorKwargs(MonoNTranslationProcessorKwargs, total=False):
    """Keyword arguments for regular translation processor initialization."""


class TranslationProcessKwargs(TranslationProcessorKwargs, total=False):
    """Keyword arguments for regular translation processing."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_translated(
    source: Series,
    source_language: Language,
    target_language: Language,
    translator: MonoNProcessor | None = None,
    **kwargs: Unpack[TranslationProcessKwargs],
) -> Series:
    """Translate subtitles between a supported language pair.

    Arguments:
        source: source-language subtitles to translate
        source_language: language of source subtitles
        target_language: target language to generate
        translator: processor to use, or None to construct one
        **kwargs: translation processor and process keyword arguments
    Returns:
        translated subtitles
    """
    stop_at_idx = kwargs.pop("stop_at_idx", None)
    if translator is None:
        translator_kwargs = cast(TranslationProcessorKwargs, kwargs)
        translator = get_translator(
            source_language,
            target_language,
            **translator_kwargs,
        )
    if stop_at_idx is None:
        return translator.process(source)
    return translator.process(source, stop_at_idx=stop_at_idx)


def get_translator(
    source_language: Language,
    target_language: Language,
    prompt_cls: type[MonoNPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> MonoNProcessor:
    """Get a regular translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt_cls: prompt class override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured translation processor
    """
    pair = (source_language, target_language)
    if pair not in _PROMPTS:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )
    if prompt_cls is None:
        prompt_cls = _PROMPTS[pair]
    if test_cases is None:
        json_paths = _JSON_PATHS[pair]
        test_cases = list(load_default_test_cases(MonoNManager, prompt_cls, json_paths))
    if provider is None:
        provider = get_provider()

    return MonoNProcessor(prompt_cls, test_cases, provider=provider, **kwargs)
