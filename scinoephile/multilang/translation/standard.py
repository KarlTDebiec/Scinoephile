#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Standard translation helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, OperationSpec, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_YUE_TRANSLATION_JSON_PATHS,
    ENG_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ENG_TRANSLATION_JSON_PATHS,
    YUE_ZHO_TRANSLATION_JSON_PATHS,
    ZHO_ENG_TRANSLATION_JSON_PATHS,
    ZHO_YUE_TRANSLATION_JSON_PATHS,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
    DualNToMPrompt,
)
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
    TranslationRoute,
    get_dual_n_to_m_processor,
    get_route,
)

__all__ = [
    "TRANSLATION_OPERATION_SPEC",
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

_REGULAR_TRANSLATION_ROUTES: dict[tuple[Language, Language], TranslationRoute] = {
    (Language.yue_hans, Language.eng): (
        ENG_YUE_TRANSLATION_JSON_PATHS,
        EngYueTranslationPrompt,
    ),
    (Language.yue_hant, Language.eng): (
        ENG_YUE_TRANSLATION_JSON_PATHS,
        EngYueTranslationPrompt,
    ),
    (Language.zho_hans, Language.eng): (
        ENG_ZHO_TRANSLATION_JSON_PATHS,
        EngZhoTranslationPrompt,
    ),
    (Language.zho_hant, Language.eng): (
        ENG_ZHO_TRANSLATION_JSON_PATHS,
        EngZhoTranslationPrompt,
    ),
    (Language.eng, Language.yue_hans): (
        YUE_ENG_TRANSLATION_JSON_PATHS,
        YueEngTranslationPromptYueHans,
    ),
    (Language.eng, Language.yue_hant): (
        YUE_ENG_TRANSLATION_JSON_PATHS,
        YueEngTranslationPromptYueHant,
    ),
    (Language.zho_hans, Language.yue_hans): (
        YUE_ZHO_TRANSLATION_JSON_PATHS,
        YueZhoTranslationPromptYueHans,
    ),
    (Language.zho_hant, Language.yue_hans): (
        YUE_ZHO_TRANSLATION_JSON_PATHS,
        YueZhoTranslationPromptYueHans,
    ),
    (Language.zho_hans, Language.yue_hant): (
        YUE_ZHO_TRANSLATION_JSON_PATHS,
        YueZhoTranslationPromptYueHant,
    ),
    (Language.zho_hant, Language.yue_hant): (
        YUE_ZHO_TRANSLATION_JSON_PATHS,
        YueZhoTranslationPromptYueHant,
    ),
    (Language.eng, Language.zho_hans): (
        ZHO_ENG_TRANSLATION_JSON_PATHS,
        ZhoEngTranslationPromptZhoHans,
    ),
    (Language.eng, Language.zho_hant): (
        ZHO_ENG_TRANSLATION_JSON_PATHS,
        ZhoEngTranslationPromptZhoHant,
    ),
    (Language.yue_hans, Language.zho_hans): (
        ZHO_YUE_TRANSLATION_JSON_PATHS,
        ZhoYueTranslationPromptZhoHans,
    ),
    (Language.yue_hant, Language.zho_hans): (
        ZHO_YUE_TRANSLATION_JSON_PATHS,
        ZhoYueTranslationPromptZhoHans,
    ),
    (Language.yue_hans, Language.zho_hant): (
        ZHO_YUE_TRANSLATION_JSON_PATHS,
        ZhoYueTranslationPromptZhoHant,
    ),
    (Language.yue_hant, Language.zho_hant): (
        ZHO_YUE_TRANSLATION_JSON_PATHS,
        ZhoYueTranslationPromptZhoHant,
    ),
}
"""Regular translation routes keyed by exact source and target languages."""


def get_translated(
    source: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNToMProcessor | None = None,
    *,
    prompt_cls: type[DualNToMPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    test_case_path: Path | None = None,
    additional_context: str | None = None,
    auto_verify: bool = False,
    stop_at_idx: int | None = None,
) -> Series:
    """Translate subtitles between a supported language pair.

    Arguments:
        source: source-language subtitles to translate
        source_language: language of source subtitles
        target_language: target language to generate
        translator: processor to use, or None to construct one
        prompt_cls: prompt class override
        test_cases: test cases
        use_dictionary_tool: whether to wire dictionary tools for compatible prompts
        provider: provider to use for queries
        test_case_path: path where encountered test cases are persisted
        additional_context: additional context to include in the system prompt
        auto_verify: whether generated test cases should be marked verified
        stop_at_idx: exclusive block index at which to stop processing
    Returns:
        translated subtitles
    """
    if translator is None:
        translator = get_translator(
            source_language,
            target_language,
            prompt_cls=prompt_cls,
            test_cases=test_cases,
            use_dictionary_tool=use_dictionary_tool,
            provider=provider,
            test_case_path=test_case_path,
            additional_context=additional_context,
            auto_verify=auto_verify,
        )
    if stop_at_idx is None:
        return translator.process(source, Series())
    return translator.process(source, Series(), stop_at_idx=stop_at_idx)


def get_translator(
    source_language: Language,
    target_language: Language,
    *,
    prompt_cls: type[DualNToMPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    test_case_path: Path | None = None,
    additional_context: str | None = None,
    auto_verify: bool = False,
) -> DualNToMProcessor:
    """Get a regular translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt_cls: prompt class override
        test_cases: test cases
        use_dictionary_tool: whether to wire dictionary tools for compatible prompts
        provider: provider to use for queries
        test_case_path: path where encountered test cases are persisted
        additional_context: additional context to include in the system prompt
        auto_verify: whether generated test cases should be marked verified
    Returns:
        configured translation processor
    """
    route = get_route(_REGULAR_TRANSLATION_ROUTES, source_language, target_language)
    return get_dual_n_to_m_processor(
        TRANSLATION_OPERATION_SPEC,
        route,
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        use_dictionary_tool=use_dictionary_tool,
        provider=provider,
        test_case_path=test_case_path,
        additional_context=additional_context,
        auto_verify=auto_verify,
    )
