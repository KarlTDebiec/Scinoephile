#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Gapped translation helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, OperationSpec, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
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
    TranslationRoute,
    get_dual_n_minus_m_to_n_processor,
    get_route,
)

__all__ = [
    "GAPPED_TRANSLATION_OPERATION_SPEC",
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


def get_gap_translated(
    source: Series,
    target: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNMinusMToNProcessor | None = None,
    *,
    prompt_cls: type[DualNMinusMToNPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    test_case_path: Path | None = None,
    additional_context: str | None = None,
    auto_verify: bool = False,
    stop_at_idx: int | None = None,
) -> Series:
    """Translate target-language subtitle gaps from source-language subtitles.

    Arguments:
        source: source-language reference subtitles
        target: target-language subtitles that may contain gaps
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
        target-language subtitles with gaps translated
    """
    if translator is None:
        translator = get_gap_translator(
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
        return translator.process(target, source)
    return translator.process(target, source, stop_at_idx=stop_at_idx)


def get_gap_translator(
    source_language: Language,
    target_language: Language,
    *,
    prompt_cls: type[DualNMinusMToNPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    test_case_path: Path | None = None,
    additional_context: str | None = None,
    auto_verify: bool = False,
) -> DualNMinusMToNProcessor:
    """Get a gap translation processor for a supported language pair.

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
        configured gapped translation processor
    """
    route = get_route(_GAPPED_TRANSLATION_ROUTES, source_language, target_language)
    return get_dual_n_minus_m_to_n_processor(
        GAPPED_TRANSLATION_OPERATION_SPEC,
        route,
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        use_dictionary_tool=use_dictionary_tool,
        provider=provider,
        test_case_path=test_case_path,
        additional_context=additional_context,
        auto_verify=auto_verify,
    )
