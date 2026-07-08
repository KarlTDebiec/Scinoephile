#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided translation helpers."""

from __future__ import annotations

from typing import Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import OperationSpec, ProcessorKwargs
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
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

from .shared import (
    DualNToMTranslationProcessorKwargs,
    TranslationRoute,
)

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

_GUIDED_TRANSLATION_ROUTES: dict[tuple[Language, Language], TranslationRoute] = {
    (Language.yue_hans, Language.eng): (
        ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        EngYueGuidedTranslationPrompt,
    ),
    (Language.yue_hant, Language.eng): (
        ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        EngYueGuidedTranslationPrompt,
    ),
    (Language.zho_hans, Language.eng): (
        ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        EngZhoGuidedTranslationPrompt,
    ),
    (Language.zho_hant, Language.eng): (
        ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        EngZhoGuidedTranslationPrompt,
    ),
    (Language.eng, Language.yue_hans): (
        YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
        YueEngGuidedTranslationPromptYueHans,
    ),
    (Language.eng, Language.yue_hant): (
        YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
        YueEngGuidedTranslationPromptYueHant,
    ),
    (Language.zho_hans, Language.yue_hans): (
        YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        YueZhoGuidedTranslationPromptYueHans,
    ),
    (Language.zho_hant, Language.yue_hans): (
        YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        YueZhoGuidedTranslationPromptYueHans,
    ),
    (Language.zho_hans, Language.yue_hant): (
        YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        YueZhoGuidedTranslationPromptYueHant,
    ),
    (Language.zho_hant, Language.yue_hant): (
        YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
        YueZhoGuidedTranslationPromptYueHant,
    ),
    (Language.eng, Language.zho_hans): (
        ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoEngGuidedTranslationPromptZhoHans,
    ),
    (Language.eng, Language.zho_hant): (
        ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoEngGuidedTranslationPromptZhoHant,
    ),
    (Language.yue_hans, Language.zho_hans): (
        ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoYueGuidedTranslationPromptZhoHans,
    ),
    (Language.yue_hant, Language.zho_hans): (
        ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoYueGuidedTranslationPromptZhoHans,
    ),
    (Language.yue_hans, Language.zho_hant): (
        ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoYueGuidedTranslationPromptZhoHant,
    ),
    (Language.yue_hant, Language.zho_hant): (
        ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
        ZhoYueGuidedTranslationPromptZhoHant,
    ),
}
"""Guided translation routes keyed by exact source and target languages."""


class GuidedTranslationProcessorKwargs(
    DualNToMTranslationProcessorKwargs,
    total=False,
):
    """Keyword arguments for guided translation processor initialization."""


class GuidedTranslationProcessKwargs(GuidedTranslationProcessorKwargs, total=False):
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
        **kwargs: translation processor and process keyword arguments
    Returns:
        guided-translated subtitles
    """
    stop_at_idx = kwargs.pop("stop_at_idx", None)
    if translator is None:
        translator_kwargs = cast(GuidedTranslationProcessorKwargs, kwargs)
        translator = get_guided_translator(
            source_language,
            target_language,
            **translator_kwargs,
        )
    if stop_at_idx is None:
        return translator.process(source, target)
    return translator.process(source, target, stop_at_idx=stop_at_idx)


def get_guided_translator(
    source_language: Language,
    target_language: Language,
    **kwargs: Unpack[GuidedTranslationProcessorKwargs],
) -> DualNToMProcessor:
    """Get a guided translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        **kwargs: processor initialization keyword arguments
    Returns:
        configured guided translation processor
    """
    route = _GUIDED_TRANSLATION_ROUTES.get((source_language, target_language))
    if route is None:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )

    json_paths, route_prompt_cls = route
    selected_prompt_cls = kwargs.pop("prompt_cls", None) or cast(
        type[DualNToMPrompt], route_prompt_cls
    )

    test_cases = kwargs.pop("test_cases", None)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                GUIDED_TRANSLATION_OPERATION_SPEC.manager_cls,
                selected_prompt_cls,
                json_paths,
            )
        )

    provider = kwargs.pop("provider", None)
    if provider is None:
        provider = get_provider()

    tool_box = kwargs.pop("tool_box", None)
    use_dictionary_tool = kwargs.pop("use_dictionary_tool", True)
    if (
        tool_box is None
        and use_dictionary_tool
        and hasattr(selected_prompt_cls, "dictionary_tool_name")
        and hasattr(selected_prompt_cls, "dictionary_tool_description")
        and hasattr(selected_prompt_cls, "dictionary_tool_query_description")
    ):
        tool_box = get_dictionary_tools(
            cast(type[DictionaryToolPrompt], selected_prompt_cls)
        )

    processor_kwargs = cast(ProcessorKwargs, kwargs)
    processor_kwargs["tool_box"] = tool_box
    return DualNToMProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **processor_kwargs,
    )
