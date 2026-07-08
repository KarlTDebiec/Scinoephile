#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided translation helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, OperationSpec, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
    DualNToMPrompt,
)
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
    TranslationRoute,
    get_dual_n_to_m_processor,
    get_route,
)

__all__ = [
    "GUIDED_TRANSLATION_OPERATION_SPEC",
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


def get_guided_translated(
    source: Series,
    target: Series,
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
    """Translate subtitles using target-language guidance.

    Arguments:
        source: source-language subtitles to translate
        target: target-language guide subtitles
        source_language: source language
        target_language: target language
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
        guided-translated subtitles
    """
    if translator is None:
        translator = get_guided_translator(
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
        return translator.process(source, target)
    return translator.process(source, target, stop_at_idx=stop_at_idx)


def get_guided_translator(
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
    """Get a guided translation processor for a supported language pair.

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
        configured guided translation processor
    """
    route = get_route(_GUIDED_TRANSLATION_ROUTES, source_language, target_language)
    return get_dual_n_to_m_processor(
        GUIDED_TRANSLATION_OPERATION_SPEC,
        route,
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        use_dictionary_tool=use_dictionary_tool,
        provider=provider,
        test_case_path=test_case_path,
        additional_context=additional_context,
        auto_verify=auto_verify,
    )
