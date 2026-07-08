#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Gapped translation helpers."""

from __future__ import annotations

from typing import Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import OperationSpec, ProcessorKwargs
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.translation import EngYueGappedTranslationPrompt
from scinoephile.multilang.eng_zho.translation import EngZhoGappedTranslationPrompt
from scinoephile.multilang.yue_eng.translation import (
    YueEngGappedTranslationPromptYueHans,
    YueEngGappedTranslationPromptYueHant,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoGappedTranslationPromptYueHans,
    YueZhoGappedTranslationPromptYueHant,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoEngGappedTranslationPromptZhoHans,
    ZhoEngGappedTranslationPromptZhoHant,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoYueGappedTranslationPromptZhoHans,
    ZhoYueGappedTranslationPromptZhoHant,
)

from .shared import (
    DualNMinusMToNTranslationProcessorKwargs,
    TranslationRoute,
)

__all__ = [
    "GAPPED_TRANSLATION_OPERATION_SPEC",
    "GappedTranslationProcessKwargs",
    "GappedTranslationProcessorKwargs",
    "get_gap_translated",
    "get_gap_translator",
]

GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="gapped-translation",
    test_case_table_name="test_cases__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=DualNMinusMToNPrompt,
)
"""Operation specification for gapped translation."""

_GAPPED_TRANSLATION_ROUTES: dict[tuple[Language, Language], TranslationRoute] = {
    (Language.yue_hans, Language.eng): (
        ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        EngYueGappedTranslationPrompt,
    ),
    (Language.yue_hant, Language.eng): (
        ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        EngYueGappedTranslationPrompt,
    ),
    (Language.zho_hans, Language.eng): (
        ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        EngZhoGappedTranslationPrompt,
    ),
    (Language.zho_hant, Language.eng): (
        ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        EngZhoGappedTranslationPrompt,
    ),
    (Language.eng, Language.yue_hans): (
        YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
        YueEngGappedTranslationPromptYueHans,
    ),
    (Language.eng, Language.yue_hant): (
        YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
        YueEngGappedTranslationPromptYueHant,
    ),
    (Language.zho_hans, Language.yue_hans): (
        YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        YueZhoGappedTranslationPromptYueHans,
    ),
    (Language.zho_hant, Language.yue_hans): (
        YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        YueZhoGappedTranslationPromptYueHans,
    ),
    (Language.zho_hans, Language.yue_hant): (
        YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        YueZhoGappedTranslationPromptYueHant,
    ),
    (Language.zho_hant, Language.yue_hant): (
        YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
        YueZhoGappedTranslationPromptYueHant,
    ),
    (Language.eng, Language.zho_hans): (
        ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoEngGappedTranslationPromptZhoHans,
    ),
    (Language.eng, Language.zho_hant): (
        ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoEngGappedTranslationPromptZhoHant,
    ),
    (Language.yue_hans, Language.zho_hans): (
        ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoYueGappedTranslationPromptZhoHans,
    ),
    (Language.yue_hant, Language.zho_hans): (
        ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoYueGappedTranslationPromptZhoHans,
    ),
    (Language.yue_hans, Language.zho_hant): (
        ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoYueGappedTranslationPromptZhoHant,
    ),
    (Language.yue_hant, Language.zho_hant): (
        ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
        ZhoYueGappedTranslationPromptZhoHant,
    ),
}
"""Gapped translation routes keyed by exact source and target languages."""


class GappedTranslationProcessorKwargs(
    DualNMinusMToNTranslationProcessorKwargs,
    total=False,
):
    """Keyword arguments for gapped translation processor initialization."""


class GappedTranslationProcessKwargs(GappedTranslationProcessorKwargs, total=False):
    """Keyword arguments for gapped translation processing."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_gap_translated(
    source: Series,
    target: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[GappedTranslationProcessKwargs],
) -> Series:
    """Translate target-language subtitle gaps from source-language subtitles.

    Arguments:
        source: source-language reference subtitles
        target: target-language subtitles that may contain gaps
        source_language: source language
        target_language: target language
        translator: processor to use, or None to construct one
        **kwargs: translation processor and process keyword arguments
    Returns:
        target-language subtitles with gaps translated
    """
    stop_at_idx = kwargs.pop("stop_at_idx", None)
    if translator is None:
        translator_kwargs = cast(GappedTranslationProcessorKwargs, kwargs)
        translator = get_gap_translator(
            source_language,
            target_language,
            **translator_kwargs,
        )
    if stop_at_idx is None:
        return translator.process(target, source)
    return translator.process(target, source, stop_at_idx=stop_at_idx)


def get_gap_translator(
    source_language: Language,
    target_language: Language,
    **kwargs: Unpack[GappedTranslationProcessorKwargs],
) -> DualNMinusMToNProcessor:
    """Get a gap translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        **kwargs: processor initialization keyword arguments
    Returns:
        configured gapped translation processor
    """
    route = _GAPPED_TRANSLATION_ROUTES.get((source_language, target_language))
    if route is None:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )

    json_paths, route_prompt_cls = route
    selected_prompt_cls = kwargs.pop("prompt_cls", None) or cast(
        type[DualNMinusMToNPrompt], route_prompt_cls
    )

    test_cases = kwargs.pop("test_cases", None)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                GAPPED_TRANSLATION_OPERATION_SPEC.manager_cls,
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
    return DualNMinusMToNProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **processor_kwargs,
    )
