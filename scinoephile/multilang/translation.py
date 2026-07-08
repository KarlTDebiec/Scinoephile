#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for translating between supported language pairs."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import LLMProvider, OperationSpec, Prompt, TestCase, ToolBox
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    ENG_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    ENG_YUE_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    ENG_ZHO_TRANSLATION_JSON_PATHS,
    YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ENG_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    YUE_ZHO_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_ENG_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_GUIDED_TRANSLATION_JSON_PATHS,
    ZHO_YUE_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
    DualNToMPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.translation import (
    EngYueGappedTranslationPrompt,
    EngYueGuidedTranslationPrompt,
    EngYueTranslationPrompt,
)
from scinoephile.multilang.eng_zho.translation import (
    EngZhoGappedTranslationPrompt,
    EngZhoGuidedTranslationPrompt,
    EngZhoTranslationPrompt,
)
from scinoephile.multilang.yue_eng.translation import (
    YueEngGappedTranslationPromptYueHans,
    YueEngGappedTranslationPromptYueHant,
    YueEngGuidedTranslationPromptYueHans,
    YueEngGuidedTranslationPromptYueHant,
    YueEngTranslationPromptYueHans,
    YueEngTranslationPromptYueHant,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoGappedTranslationPromptYueHans,
    YueZhoGappedTranslationPromptYueHant,
    YueZhoGuidedTranslationPromptYueHans,
    YueZhoGuidedTranslationPromptYueHant,
    YueZhoTranslationPromptYueHans,
    YueZhoTranslationPromptYueHant,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoEngGappedTranslationPromptZhoHans,
    ZhoEngGappedTranslationPromptZhoHant,
    ZhoEngGuidedTranslationPromptZhoHans,
    ZhoEngGuidedTranslationPromptZhoHant,
    ZhoEngTranslationPromptZhoHans,
    ZhoEngTranslationPromptZhoHant,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoYueGappedTranslationPromptZhoHans,
    ZhoYueGappedTranslationPromptZhoHant,
    ZhoYueGuidedTranslationPromptZhoHans,
    ZhoYueGuidedTranslationPromptZhoHant,
    ZhoYueTranslationPromptZhoHans,
    ZhoYueTranslationPromptZhoHant,
)

__all__ = [
    "GAPPED_TRANSLATION_OPERATION_SPEC",
    "GUIDED_TRANSLATION_OPERATION_SPEC",
    "TRANSLATION_OPERATION_SPEC",
    "get_gap_translated",
    "get_gapped_translator",
    "get_guided_translated",
    "get_guided_translator",
    "get_translated",
    "get_translator",
]

type _TranslationRoute = tuple[tuple[Path, ...], type[Prompt]]

TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="translation",
    test_case_table_name="test_cases__translation",
    manager_cls=DualNToMManager,
    prompt_cls=DualNToMPrompt,
)
"""Operation specification for regular translation."""

GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="gapped-translation",
    test_case_table_name="test_cases__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=DualNMinusMToNPrompt,
)
"""Operation specification for gapped translation."""

GUIDED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="guided-translation",
    test_case_table_name="test_cases__guided_translation",
    manager_cls=DualNToMManager,
    prompt_cls=DualNToMPrompt,
)
"""Operation specification for guided translation."""

_REGULAR_TRANSLATION_ROUTES: dict[tuple[Language, Language], _TranslationRoute] = {
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

_GAPPED_TRANSLATION_ROUTES: dict[tuple[Language, Language], _TranslationRoute] = {
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

_GUIDED_TRANSLATION_ROUTES: dict[tuple[Language, Language], _TranslationRoute] = {
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
    route = _get_route(_REGULAR_TRANSLATION_ROUTES, source_language, target_language)
    return _get_dual_n_to_m_processor(
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
        translator = get_gapped_translator(
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


def get_gapped_translator(
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
    """Get a gapped translation processor for a supported language pair.

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
    route = _get_route(_GAPPED_TRANSLATION_ROUTES, source_language, target_language)
    return _get_dual_n_minus_m_to_n_processor(
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
    route = _get_route(_GUIDED_TRANSLATION_ROUTES, source_language, target_language)
    return _get_dual_n_to_m_processor(
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


def _get_dual_n_minus_m_to_n_processor(
    operation_spec: OperationSpec,
    route: _TranslationRoute,
    *,
    prompt_cls: type[DualNMinusMToNPrompt] | None,
    test_cases: list[TestCase] | None,
    use_dictionary_tool: bool,
    provider: LLMProvider | None,
    test_case_path: Path | None,
    additional_context: str | None,
    auto_verify: bool,
) -> DualNMinusMToNProcessor:
    """Get a DualNMinusMToNProcessor from route and caller configuration."""
    json_paths, route_prompt_cls = route
    selected_prompt_cls = prompt_cls
    if selected_prompt_cls is None:
        selected_prompt_cls = cast(type[DualNMinusMToNPrompt], route_prompt_cls)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                operation_spec.manager_cls,
                selected_prompt_cls,
                json_paths,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNMinusMToNProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        provider=provider,
        additional_context=additional_context,
        auto_verify=auto_verify,
        tool_box=_get_tool_box(selected_prompt_cls, use_dictionary_tool),
    )


def _get_dual_n_to_m_processor(
    operation_spec: OperationSpec,
    route: _TranslationRoute,
    *,
    prompt_cls: type[DualNToMPrompt] | None,
    test_cases: list[TestCase] | None,
    use_dictionary_tool: bool,
    provider: LLMProvider | None,
    test_case_path: Path | None,
    additional_context: str | None,
    auto_verify: bool,
) -> DualNToMProcessor:
    """Get a DualNToMProcessor from route and caller configuration."""
    json_paths, route_prompt_cls = route
    selected_prompt_cls = prompt_cls
    if selected_prompt_cls is None:
        selected_prompt_cls = cast(type[DualNToMPrompt], route_prompt_cls)
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                operation_spec.manager_cls,
                selected_prompt_cls,
                json_paths,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNToMProcessor(
        prompt_cls=selected_prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        provider=provider,
        additional_context=additional_context,
        auto_verify=auto_verify,
        tool_box=_get_tool_box(selected_prompt_cls, use_dictionary_tool),
    )


def _get_route(
    routes: dict[tuple[Language, Language], _TranslationRoute],
    source_language: Language,
    target_language: Language,
) -> _TranslationRoute:
    """Get the route for a supported source and target language."""
    route = routes.get((source_language, target_language))
    if route is None:
        raise ScinoephileError(
            f"Unsupported translation pair: {source_language.tag} to "
            f"{target_language.tag}"
        )
    return route


def _get_tool_box(
    prompt_cls: type[Prompt],
    use_dictionary_tool: bool,
) -> ToolBox | None:
    """Get dictionary tools for compatible prompts when requested."""
    if not use_dictionary_tool:
        return None
    if not _has_dictionary_tool_prompt(prompt_cls):
        return None
    return get_dictionary_tools(cast(type[DictionaryToolPrompt], prompt_cls))


def _has_dictionary_tool_prompt(prompt_cls: type[Prompt]) -> bool:
    """Return whether a prompt class provides dictionary tool text."""
    return (
        hasattr(prompt_cls, "dictionary_tool_name")
        and hasattr(prompt_cls, "dictionary_tool_description")
        and hasattr(prompt_cls, "dictionary_tool_query_description")
    )
