#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Standard translation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import OperationSpec, ProcessorKwargs
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    ENG_YUE_TRANSLATION_JSON_PATHS,
    ENG_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ENG_TRANSLATION_JSON_PATHS,
    YUE_ZHO_TRANSLATION_JSON_PATHS,
    ZHO_ENG_TRANSLATION_JSON_PATHS,
    ZHO_YUE_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
    DualNToMPrompt,
)
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

from .shared import (
    DualNToMTranslationProcessorKwargs,
)

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
    manager_cls=DualNToMManager,
    prompt_cls=DualNToMPrompt,
)
"""Operation specification for regular translation."""


_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.yue_hans, Language.eng): ENG_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.eng): ENG_YUE_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.eng): ENG_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.eng): ENG_ZHO_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hans): YUE_ENG_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hant): YUE_ENG_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hans): YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hans): YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hant): YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hant): YUE_ZHO_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hans): ZHO_ENG_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hant): ZHO_ENG_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hans): ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hans): ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): ZHO_YUE_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): ZHO_YUE_TRANSLATION_JSON_PATHS,
}
"""Regular translation JSON paths keyed by exact source and target languages."""

_PROMPTS: dict[tuple[Language, Language], type[DualNToMPrompt]] = {
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


class TranslationProcessorKwargs(DualNToMTranslationProcessorKwargs, total=False):
    """Keyword arguments for regular translation processor initialization."""


class TranslationProcessKwargs(TranslationProcessorKwargs, total=False):
    """Keyword arguments for regular translation processing."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_translated(
    source: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNToMProcessor | None = None,
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
        return translator.process(source, Series())
    return translator.process(source, Series(), stop_at_idx=stop_at_idx)


def get_translator(
    source_language: Language,
    target_language: Language,
    **kwargs: Unpack[TranslationProcessorKwargs],
) -> DualNToMProcessor:
    """Get a regular translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        **kwargs: processor initialization keyword arguments
    Returns:
        configured translation processor
    """
    json_paths = _JSON_PATHS.get((source_language, target_language))
    route_prompt_cls = _PROMPTS.get((source_language, target_language))
    if json_paths is None or route_prompt_cls is None:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )
    prompt_cls = kwargs.pop("prompt_cls", None) or route_prompt_cls
    test_cases = kwargs.pop("test_cases", None)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(DualNToMManager, prompt_cls, json_paths)
        )
    provider = kwargs.pop("provider", None) or get_provider()

    tool_box = kwargs.pop("tool_box", None)
    use_dictionary_tool = kwargs.pop("use_dictionary_tool", True)
    if (
        tool_box is None
        and use_dictionary_tool
        and hasattr(prompt_cls, "dictionary_tool_name")
        and hasattr(prompt_cls, "dictionary_tool_description")
        and hasattr(prompt_cls, "dictionary_tool_query_description")
    ):
        tool_box = get_dictionary_tools(cast(type[DictionaryToolPrompt], prompt_cls))

    processor_kwargs = cast(ProcessorKwargs, kwargs)
    processor_kwargs["tool_box"] = tool_box
    return DualNToMProcessor(
        prompt_cls,
        test_cases,
        provider=provider,
        **processor_kwargs,
    )
